"""
Blockchain-based tamper-proof audit logging for MedScope.
- Each block contains: index, previous_hash, timestamp, payload, hash (SHA-256 of index+previous_hash+timestamp+payload).
- Changing any past block would change its hash and break the chain (tamper-evident).
- Logs: inventory add/update/remove, quantity changes, discount set/remove, expiry date changes.
- Does not replace the primary database; append-only audit trail only.
"""
import hashlib
import json
from datetime import datetime
from typing import Any, Optional

# Firestore client injected by app
_db = None

def init_audit(db_client):
    """Call from app.py after Firestore is initialized."""
    global _db
    _db = db_client


def _serialize(obj: Any) -> Any:
    """Make payload JSON-serializable for hashing."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize(x) for x in obj]
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def _get_chain_meta():
    """Get last block index and hash. Creates meta doc if missing."""
    if not _db:
        return None
    ref = _db.collection("audit_chain_meta").document("state")
    doc = ref.get()
    if doc and doc.exists:
        d = doc.to_dict()
        return d.get("last_index", -1), d.get("last_hash", "0")
    ref.set({"last_index": -1, "last_hash": "0"})
    return -1, "0"


def _append_block(payload: dict) -> bool:
    """Append one block to the chain. Returns True on success."""
    if not _db:
        return False
    try:
        last_index, last_hash = _get_chain_meta()
        if last_index is None:
            return False
        index = last_index + 1
        timestamp = datetime.utcnow().isoformat() + "Z"
        payload_ser = _serialize(payload)
        payload_str = json.dumps(payload_ser, sort_keys=True)
        block_data = f"{index}{last_hash}{timestamp}{payload_str}"
        block_hash = hashlib.sha256(block_data.encode("utf-8")).hexdigest()
        block = {
            "index": index,
            "previous_hash": last_hash,
            "timestamp": timestamp,
            "payload": payload_ser,
            "hash": block_hash,
        }
        _db.collection("audit_chain").document(f"block_{index}").set(block)
        _db.collection("audit_chain_meta").document("state").set({
            "last_index": index,
            "last_hash": block_hash,
        }, merge=True)
        return True
    except Exception as e:
        print("❌ Audit block append error:", e)
        return False


def log_inventory_change(
    pharmacy_email: str,
    entity_id: str,
    action: str,
    before: Optional[dict] = None,
    after: Optional[dict] = None,
    extra: Optional[dict] = None,
) -> bool:
    """
    Log an inventory update (add/update/remove/quantity change).
    action: "add" | "update" | "remove" | "quantity_change"
    """
    payload = {
        "type": "inventory",
        "pharmacy_email": pharmacy_email,
        "entity_id": entity_id,
        "action": action,
        "before": _serialize(before) if before else None,
        "after": _serialize(after) if after else None,
        **(extra or {}),
    }
    return _append_block(payload)


def log_discount_change(
    pharmacy_email: str,
    entity_id: str,
    action: str,
    before: Optional[dict] = None,
    after: Optional[dict] = None,
) -> bool:
    """
    Log a discount add/modify/remove (tamper-proof audit).
    action: "set" | "remove"
    """
    payload = {
        "type": "discount",
        "pharmacy_email": pharmacy_email,
        "entity_id": entity_id,
        "action": action,
        "before": _serialize(before) if before else None,
        "after": _serialize(after) if after else None,
    }
    return _append_block(payload)


def log_expiry_change(
    pharmacy_email: str,
    entity_id: str,
    old_expiry: Optional[str],
    new_expiry: Optional[str],
    extra: Optional[dict] = None,
) -> bool:
    """
    Log when a pharmacy changes expiry date (tamper-proof audit).
    Detects intentional or accidental expiry tampering.
    """
    payload = {
        "type": "expiry_change",
        "pharmacy_email": pharmacy_email,
        "entity_id": entity_id,
        "action": "expiry_change",
        "before": {"expiry": old_expiry},
        "after": {"expiry": new_expiry},
        **(extra or {}),
    }
    return _append_block(payload)


def verify_chain():
    """
    Verify the audit chain: recompute each block's hash and check it matches.
    If any block was tampered with (e.g. invoice/expiry data changed in Firestore),
    the hash will not match and the chain is broken.
    Returns: (is_valid: bool, broken_index: Optional[int])
    """
    if not _db:
        return True, None
    try:
        meta = _db.collection("audit_chain_meta").document("state").get()
        if not meta or not meta.exists:
            return True, None
        last_index = meta.to_dict().get("last_index", -1)
        if last_index < 0:
            return True, None
        prev_hash = "0"
        for i in range(last_index + 1):
            block_ref = _db.collection("audit_chain").document(f"block_{i}")
            block_doc = block_ref.get()
            if not block_doc or not block_doc.exists:
                return False, i
            block = block_doc.to_dict()
            payload_ser = block.get("payload")
            index = block.get("index", i)
            timestamp = block.get("timestamp", "")
            stored_hash = block.get("hash", "")
            payload_str = json.dumps(payload_ser, sort_keys=True) if payload_ser is not None else "null"
            block_data = f"{index}{prev_hash}{timestamp}{payload_str}"
            computed_hash = hashlib.sha256(block_data.encode("utf-8")).hexdigest()
            if computed_hash != stored_hash:
                return False, i
            prev_hash = stored_hash
        return True, None
    except Exception as e:
        print("❌ verify_chain error:", e)
        return False, 0
