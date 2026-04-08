# app.py
<<<<<<< HEAD


=======
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
from flask import (
    Flask, render_template, request, redirect, url_for, jsonify, Response, send_file, session
)
from fpdf import FPDF
import os
import pandas as pd
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from math import radians, sin, cos, sqrt, atan2
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from functools import wraps
import json
<<<<<<< HEAD
import re
=======
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54

# ---------------- ENVIRONMENT ---------------- 
load_dotenv()
# Load .env.example if .env does not exist (so default keys exist)
if not os.path.exists(".env") and os.path.exists(".env.example"):
    load_dotenv(".env.example")
GMAIL_SENDER = (os.getenv("GMAIL_SENDER") or "").strip()
_raw_password = os.getenv("GMAIL_APP_PASSWORD") or ""
# Gmail App Passwords may be pasted with spaces; strip for SMTP
GMAIL_APP_PASSWORD = "".join(_raw_password.split()) if _raw_password else ""
ADMIN_EMAIL = (os.getenv("ADMIN_EMAIL") or "").strip()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "medscope-secret-key-change-in-production")

# ---------------- FIRESTORE INIT ---------------- 
db = None
auth = None
try:
    if os.path.exists("serviceAccountKey.json"):
        import firebase_admin
        from firebase_admin import credentials, firestore, auth as firebase_auth
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        auth = firebase_auth
        print("✅ Firestore initialized.")
    else:
        print("⚠️ No serviceAccountKey.json found — running in CSV fallback mode.")
except Exception as e:
    print("❌ Firestore init error:", e)
    db = None
    auth = None

if db:
    try:
        import blockchain_audit
        blockchain_audit.init_audit(db)
        print("✅ Blockchain audit logging enabled.")
    except Exception as e:
        print("⚠️ Blockchain audit init skipped:", e)

# ---------------- AUTHENTICATION HELPERS ---------------- 
def get_user_role(email):
    """Get user role from Firestore users collection"""
    if not db or not email:
        return None
    try:
        user_doc = db.collection("users").document(email).get()
        if user_doc.exists:
            return user_doc.to_dict().get("role")
        return None
    except Exception:
        return None

def login_required(role=None):
    """Decorator to require login and optionally check role"""
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            user_email = session.get("user_email")
            user_role = session.get("user_role")
            
            if not user_email:
                return redirect(url_for("login"))
            
            if role and user_role != role:
                return redirect(url_for("home")), 403
            
            return func(*args, **kwargs)
        return wrapped
    return decorator

def guest_allowed(func):
    """Decorator to allow guest access (no login required)"""
    @wraps(func)
    def wrapped(*args, **kwargs):
        # Allow access without login - guest mode
        return func(*args, **kwargs)
    return wrapped

# ---------------- HELPERS ---------------- 
def load_sample_data():
    pharm_df = pd.read_csv("sample_csvs/hyd_pharmacies.csv")
    med_df = pd.read_csv("sample_csvs/erp_bulk_medicines.csv")
    return pharm_df, med_df

def get_status(expiry_str):
    try:
        ed = datetime.strptime(str(expiry_str), "%Y-%m-%d").date()
        if ed < date.today():
            return "Expired"
        elif (ed - date.today()).days <= 30:
            return "Expiring Soon"
        else:
            return "Available"
    except Exception:
        return "Unknown"

def send_email(to_email, subject, body, cc=None):
    """
    Send email using GMAIL_SENDER (From). Recipient (To) = to_email (e.g. pharmacy's registered email).
    If cc is set (e.g. ADMIN_EMAIL), that address gets a copy. Used for expiry alerts: system sends TO each pharmacy at their registered email; admin can be CC'd.
    """
    import smtplib
    from email.mime.text import MIMEText

    if not GMAIL_SENDER or not GMAIL_APP_PASSWORD:
        print("⚠️ Email not configured; set GMAIL_SENDER and GMAIL_APP_PASSWORD in .env")
        return False

    to_email = (to_email or "").strip()
    if not to_email:
        print("⚠️ send_email: no recipient.")
        return False

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_SENDER
    msg["To"] = to_email
    if cc:
        msg["Cc"] = cc
    recipients = [r for r in [to_email, cc] if r]

    # Try SMTP_SSL (port 465) first, then SMTP + STARTTLS (port 587)
    for attempt, (use_ssl, port) in enumerate([(True, 465), (False, 587)]):
        try:
            if use_ssl:
                server = smtplib.SMTP_SSL("smtp.gmail.com", port, timeout=15)
            else:
                server = smtplib.SMTP("smtp.gmail.com", port, timeout=15)
                server.ehlo()
                server.starttls()
                server.ehlo()
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_SENDER, recipients, msg.as_string())
            server.quit()
            print("📧 Email sent to", to_email)
            return True
        except Exception as e:
            kind = "SMTP_SSL(465)" if use_ssl else "SMTP_STARTTLS(587)"
            print(f"Email send error ({kind}):", e)
    return False

<<<<<<< HEAD

def send_discount_alerts(medicine_name, discount_value, discount_type, valid_till):
    """Send email alerts to users interested in this medicine when discount is added"""

    if not db:
        return

    try:
        users = db.collection("user_medicine_interests") \
            .where("medicine_name", "==", medicine_name).stream()

        for u in users:
            data = u.to_dict()
            user_email = data.get("email")

            if not user_email:
                continue

            subject = f"💊 Discount Alert for {medicine_name}"

            if discount_type == "percentage":
                discount_text = f"{discount_value}% OFF"
            else:
                discount_text = f"₹{discount_value} OFF"

            body = f"""
Hello,

Good news! 🎉

A discount has been added for the medicine you are tracking.

Medicine: {medicine_name}
Discount: {discount_text}
Valid Till: {valid_till}

Visit MedScope to order now.

Regards,
MedScope Team
"""

            send_email(user_email, subject, body)

    except Exception as e:
        print("Discount alert error:", e)

=======
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
def send_sms(phone_number, message):
    """Send SMS using free service (placeholder - can use Twilio trial or similar)"""
    # For now, just log it. User can integrate free SMS service later
    print(f"📱 SMS to {phone_number}: {message}")
    return True

<<<<<<< HEAD
def normalize_medicine_query(s):
    """Normalize for case-insensitive, flexible matching (dolo-650, DOLO650, dolo 650 all match Dolo-650)."""
    if not s:
        return ""
    return "".join(c for c in str(s).lower().replace(" ", "").replace("-", "") if c.isalnum())


=======
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def apply_discount(price_per_unit, med, as_of_date=None):
    """Apply discount from medicine doc if valid. Returns (effective_price_per_unit, discount_applied)."""
    as_of_date = as_of_date or date.today()
    discount_value = med.get("discount_value")
    discount_type = (med.get("discount_type") or "percentage").strip().lower()
    valid_till = med.get("discount_valid_till") or ""
    if discount_value is None or valid_till == "":
        return float(price_per_unit), False
    try:
        valid_date = datetime.strptime(str(valid_till).strip()[:10], "%Y-%m-%d").date()
    except Exception:
        return float(price_per_unit), False
    if valid_date < as_of_date:
        return float(price_per_unit), False
    price = float(price_per_unit)
    try:
        val = float(discount_value)
    except (TypeError, ValueError):
        return price, False
    if discount_type == "flat":
        return max(0.0, price - val), True
    # percentage
    return max(0.0, price * (1 - val / 100.0)), True

# ---------------- AUTHENTICATION ROUTES ---------------- 
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "user").strip()
        
        if not email or not password:
            return render_template("login.html", error="Email and password required", role=role)
        
        # For demo: Simple authentication (in production, use Firebase Auth)
        # Check if user exists in Firestore
        if db:
            user_doc = db.collection("users").document(email).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                # In production, verify password hash. For now, simple check
                if user_data.get("password") == password and user_data.get("role") == role:
                    # Pharmacy: allow login only if admin has approved
                    if role == "pharmacy":
                        pid = email.replace("@", "_at_").replace(".", "_dot_")
                        pharm_doc = db.collection("pharmacies").document(pid).get()
                        if pharm_doc.exists:
                            status = (pharm_doc.to_dict() or {}).get("pharmacy_status") or "approved"
                            if status != "approved":
                                return render_template(
                                    "login.html",
                                    error="Your pharmacy registration is pending approval. Contact admin.",
                                    role=role,
                                )
                    session["user_email"] = email
                    session["user_role"] = role
<<<<<<< HEAD
                    session["user_name"] = user_data.get("name") or email.split("@")[0]
                    session["user_phone"] = user_data.get("phone", "")
                    next_url = request.form.get("next") or request.args.get("next") or ""
                    if next_url and next_url.startswith("/"):
                        return redirect(next_url)
=======
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
                    if role == "admin":
                        return redirect(url_for("admin"))
                    elif role == "pharmacy":
                        return redirect(url_for("pharmacy"))
                    else:
                        return redirect(url_for("user_search"))
                else:
                    return render_template("login.html", error="Invalid credentials or role mismatch", role=role)
            else:
                return render_template("login.html", error="User not found. Please register first.", role=role)
        else:
<<<<<<< HEAD
            session["user_email"] = email
            session["user_role"] = role
            session["user_name"] = email.split("@")[0]
            session["user_phone"] = ""
            next_url = request.form.get("next") or request.args.get("next") or ""
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
=======
            # Fallback for demo
            session["user_email"] = email
            session["user_role"] = role
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
            if role == "admin":
                return redirect(url_for("admin"))
            elif role == "pharmacy":
                return redirect(url_for("pharmacy"))
            else:
                return redirect(url_for("user_search"))
    
    role = request.args.get("role", "user")
<<<<<<< HEAD
    next_param = request.args.get("next", "")
    error_msg = request.args.get("error_msg")
    return render_template("login.html", role=role, error=error_msg, next=next_param)
=======
    error_msg = request.args.get("error_msg")
    return render_template("login.html", role=role, error=error_msg)
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54

@app.route("/register", methods=["GET", "POST"])
def register():
    # Admin accounts cannot be registered publicly
    role = request.args.get("role", "user") if request.method == "GET" else request.form.get("role", "user").strip()
    if role == "admin":
        return redirect(url_for("login", role="admin", error_msg="Admin accounts cannot be registered. Contact system administrator."))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "user").strip()
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        
        if role == "admin":
            return redirect(url_for("login", role="admin"))
        if not email or not password or not role:
            return render_template("register.html", error="All fields required", role=role)
        
        if db:
            # Check if user already exists
            user_doc = db.collection("users").document(email).get()
            if user_doc.exists:
                return render_template("register.html", error="User already exists. Please login.", role=role)
            
            # Create user
            user_data = {
                "email": email,
                "password": password,  # In production, hash this
                "role": role,
                "name": name,
                "phone": phone,
                "created_at": datetime.now().isoformat()
            }
            
            # If pharmacy, create pharmacy entry with PENDING status (requires admin approval)
            if role == "pharmacy":
                pid = email.replace("@", "_at_").replace(".", "_dot_")
                license_number = request.form.get("license_number", "").strip()
<<<<<<< HEAD
                license_document_path = None
                license_file = request.files.get("license_document")
                if license_file and license_file.filename:
                    ext = os.path.splitext(license_file.filename)[1].lower()
                    if ext in (".pdf", ".jpg", ".jpeg", ".png"):
                        os.makedirs("static/uploads/license", exist_ok=True)
                        safe_name = f"{pid}_{datetime.now().strftime('%Y%m%d%H%M')}{ext}"
                        filepath = os.path.join("static", "uploads", "license", safe_name)
                        license_file.save(filepath)
                        license_document_path = f"uploads/license/{safe_name}"
=======
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
                pharm_data = {
                    "pharmacy_email": email,
                    "pharmacy_name": name or email.split("@")[0],
                    "address": request.form.get("address", "").strip(),
                    "lat": float(request.form.get("lat", 17.3850)),
                    "lon": float(request.form.get("lon", 78.4867)),
                    "phone": phone,
                    "license_number": license_number,
                    "pharmacy_status": "pending",  # Must be approved by admin before login
                    "created_at": datetime.now().isoformat(),
                }
<<<<<<< HEAD
                if license_document_path:
                    pharm_data["license_document_path"] = license_document_path
=======
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
                db.collection("pharmacies").document(pid).set(pharm_data, merge=True)
            
            db.collection("users").document(email).set(user_data)
            return redirect(url_for("login", role=role))
        else:
            return render_template("register.html", error="Database not available. Please configure Firestore.", role=role)
    
    role = request.args.get("role", "user")
    return render_template("register.html", role=role)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------------- HOME ---------------- 
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- PHARMACY DASHBOARD ---------------- 
@app.route("/pharmacy", methods=["GET", "POST"])
@login_required(role="pharmacy")
def pharmacy():
    pharmacy_email = session.get("user_email")
    
    if request.method == "POST":
        name = request.form.get("medicine", "").strip()
        try:
            qty = int(request.form.get("quantity", "0"))
        except Exception:
            qty = 0
        expiry = request.form.get("expiry", "").strip()
        
        # Use logged-in pharmacy email
        if not pharmacy_email:
            return redirect(url_for("login", role="pharmacy"))

        try:
            datetime.strptime(expiry, "%Y-%m-%d")
        except Exception:
            return "Invalid expiry format. Use YYYY-MM-DD", 400

        status = get_status(expiry)
        doc_id = f"{name}_{pharmacy_email}".replace(" ", "_")
        doc = {"name": name, "quantity": qty, "expiry": expiry, "status": status, "pharmacy_email": pharmacy_email}

        if db:
            old_snap = db.collection("medicines").document(doc_id).get()
            old_dict = old_snap.to_dict() if old_snap and old_snap.exists else None
            old_expiry = (old_dict or {}).get("expiry")
            db.collection("medicines").document(doc_id).set(doc, merge=True)
            try:
                import blockchain_audit
                blockchain_audit.log_inventory_change(
                    pharmacy_email, doc_id,
                    "update" if old_snap and old_snap.exists else "add",
                    before=old_dict,
                    after=doc,
                )
                if old_expiry is not None and str(old_expiry) != str(expiry):
                    blockchain_audit.log_expiry_change(
                        pharmacy_email, doc_id, old_expiry, expiry,
                        extra={"medicine_name": name},
                    )
            except Exception:
                pass
        else:
            med_df = pd.read_csv("sample_csvs/erp_bulk_medicines.csv")
            med_df = med_df.append(
                {
                    "medicine_name": name,
                    "batch_no": "BTX",
                    "quantity": qty,
                    "expiry_date": expiry,
                    "distributor_name": "Demo",
                    "purchase_date": datetime.now().strftime("%Y-%m-%d"),
                    "pharmacy_email": pharmacy_email,
                },
                ignore_index=True,
            )
            med_df.to_csv("sample_csvs/erp_bulk_medicines.csv", index=False)
        return redirect(url_for("pharmacy"))

    # Get medicines for logged-in pharmacy only
    meds = []
    counts = {"Available": 0, "Expiring Soon": 0, "Expired": 0}
    
    if db:
        for d in db.collection("medicines").where("pharmacy_email", "==", pharmacy_email).stream():
            item = d.to_dict()
            item["doc_id"] = d.id
            item["status"] = get_status(item.get("expiry", ""))
            meds.append(item)
            if item["status"] in counts:
                counts[item["status"]] += 1
    else:
        _, med_df = load_sample_data()
        for _, row in med_df.iterrows():
            if str(row.get("pharmacy_email", "")).strip() == pharmacy_email:
                med = {
                    "name": row["medicine_name"],
                    "quantity": int(row["quantity"]),
                    "expiry": row["expiry_date"],
                    "pharmacy_email": row["pharmacy_email"],
                    "status": get_status(row["expiry_date"]),
                }
                meds.append(med)
                if med["status"] in counts:
                    counts[med["status"]] += 1
    
    return render_template("pharmacy_dashboard.html", medicines=meds, counts=counts, message=None, pharmacy_email=pharmacy_email)

# ---------------- UPLOAD SIMPLE CSV ---------------- 
@app.route("/upload_csv", methods=["POST"])
@login_required(role="pharmacy")
def upload_csv():
    pharmacy_email = session.get("user_email")
    if not db:
        return render_template("pharmacy_dashboard.html", message="❌ Firestore not enabled. Use ERP CSV or CSV fallback.", medicines=[], counts={"Available": 0, "Expiring Soon": 0, "Expired": 0}, pharmacy_email=pharmacy_email)

    file = request.files.get("file")
    if not file:
        return render_template("pharmacy_dashboard.html", message="❌ No file uploaded.", medicines=[], counts={"Available": 0, "Expiring Soon": 0, "Expired": 0}, pharmacy_email=pharmacy_email)

    try:
        df = pd.read_csv(file)
        added = 0
        updated = 0
        for _, row in df.iterrows():
            name = str(row.get("name", "")).strip()
            expiry = str(row.get("expiry", "")).strip()
            email = str(row.get("pharmacy_email", pharmacy_email)).strip()  # Use logged-in pharmacy
            try:
                quantity = int(row.get("quantity", 0))
            except Exception:
                quantity = 0
            if not name or not email:
                continue
            status = get_status(expiry)
            doc_id = f"{name}_{email}".replace(" ", "_")
            doc_ref = db.collection("medicines").document(doc_id)
            old_doc = doc_ref.get()
            if old_doc.exists:
                old_expiry = (old_doc.to_dict() or {}).get("expiry")
                doc_ref.update({"quantity": quantity, "expiry": expiry, "status": status})
                updated += 1
                try:
                    import blockchain_audit
                    if old_expiry is not None and str(old_expiry) != str(expiry):
                        blockchain_audit.log_expiry_change(
                            pharmacy_email, doc_id, old_expiry, expiry,
                            extra={"medicine_name": name, "source": "upload_csv"},
                        )
                except Exception:
                    pass
            else:
                db.collection("medicines").document(doc_id).set(
                    {"name": name, "quantity": quantity, "expiry": expiry, "status": status, "pharmacy_email": email}
                )
                added += 1
        try:
            import blockchain_audit
            blockchain_audit.log_inventory_change(
                pharmacy_email, "bulk_csv",
                "bulk_upload",
                extra={"added": added, "updated": updated, "source": "upload_csv"},
            )
        except Exception:
            pass
        return redirect(url_for("pharmacy"))
    except Exception as e:
        return render_template("pharmacy_dashboard.html", message=f"❌ Error: {e}", medicines=[], counts={"Available": 0, "Expiring Soon": 0, "Expired": 0}, pharmacy_email=pharmacy_email)

# ---------------- UPLOAD ERP CSV ---------------- 
@app.route("/upload_erp_csv", methods=["POST"])
@login_required(role="pharmacy")
def upload_erp_csv():
    pharmacy_email = session.get("user_email")
    file = request.files.get("file")
    if not file:
        return "No file uploaded", 400
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return f"CSV read error: {e}", 400

    expected = [
        "medicine_name",
        "batch_no",
        "quantity",
        "expiry_date",
        "distributor_name",
        "purchase_date",
        "pharmacy_email",
    ]
    if not all(col in df.columns for col in expected):
        return f"CSV must have columns: {expected}", 400

    count = 0
    for _, row in df.iterrows():
        try:
            name = str(row["medicine_name"]).strip()
            batch = str(row["batch_no"]).strip()
            qty = int(row["quantity"])
            expiry = str(row["expiry_date"]).strip()
            dist = str(row["distributor_name"]).strip()
            purchase = str(row["purchase_date"]).strip()
            email = str(row.get("pharmacy_email", pharmacy_email)).strip()  # Use logged-in pharmacy
        except Exception:
            continue

        doc = {
            "name": name,
            "batch_no": batch,
            "quantity": qty,
            "expiry": expiry,
            "distributor_name": dist,
            "purchase_date": purchase,
            "pharmacy_email": email,
            "status": get_status(expiry),
        }
        doc_id = f"{name}_{batch}_{email}".replace(" ", "_")
        if db:
            doc_ref = db.collection("medicines").document(doc_id)
            old_doc = doc_ref.get()
            old_expiry = (old_doc.to_dict() or {}).get("expiry") if old_doc.exists else None
            doc_ref.set(doc, merge=True)
            if old_expiry is not None and str(old_expiry) != str(expiry):
                try:
                    import blockchain_audit
                    blockchain_audit.log_expiry_change(
                        pharmacy_email, doc_id, old_expiry, expiry,
                        extra={"medicine_name": name, "source": "upload_erp_csv"},
                    )
                except Exception:
                    pass
        else:
            med_df = pd.read_csv("sample_csvs/erp_bulk_medicines.csv")
            med_df = med_df.append(
                {
                    "medicine_name": name,
                    "batch_no": batch,
                    "quantity": qty,
                    "expiry_date": expiry,
                    "distributor_name": dist,
                    "purchase_date": purchase,
                    "pharmacy_email": email,
                },
                ignore_index=True,
            )
            med_df.to_csv("sample_csvs/erp_bulk_medicines.csv", index=False)
        count += 1

    if db and count > 0:
        try:
            import blockchain_audit
            blockchain_audit.log_inventory_change(
                pharmacy_email, "bulk_erp_csv",
                "bulk_upload",
                extra={"count": count, "source": "upload_erp_csv"},
            )
        except Exception:
            pass
    return f"✅ Uploaded {count} medicines (expiry checked).", 200

# ---------------- UPLOAD PHARMACIES CSV ---------------- 
@app.route("/upload_pharmacies_csv", methods=["POST"])
@login_required(role="admin")
def upload_pharmacies_csv():
    file = request.files.get("file")
    if not file:
        return "No file uploaded", 400
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return f"CSV read error: {e}", 400

    required = ["pharmacy_email", "pharmacy_name", "address", "lat", "lon"]
    if not all(col in df.columns for col in required):
        return f"CSV must have columns: {required}", 400

    count = 0
    for _, row in df.iterrows():
        email = str(row["pharmacy_email"]).strip()
        pid = email.replace("@", "_at_").replace(".", "_dot_")
        doc = {
            "pharmacy_email": email,
            "pharmacy_name": str(row["pharmacy_name"]),
            "address": str(row["address"]),
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
        }
        if db:
            db.collection("pharmacies").document(pid).set(doc, merge=True)
        else:
            pharm_df = pd.read_csv("sample_csvs/hyd_pharmacies.csv")
            if pharm_df[pharm_df["pharmacy_email"] == email].empty:
                pharm_df = pharm_df.append(
                    {
                        "pharmacy_email": email,
                        "pharmacy_name": doc["pharmacy_name"],
                        "address": doc["address"],
                        "lat": doc["lat"],
                        "lon": doc["lon"],
                    },
                    ignore_index=True,
                )
                pharm_df.to_csv("sample_csvs/hyd_pharmacies.csv", index=False)
        count += 1

    return f"✅ Uploaded {count} pharmacies successfully!", 200

# ---------------- USER SEARCH ---------------- 
@app.route("/user", methods=["GET", "POST"])
@guest_allowed
def user_search():
    results = []
    if request.method == "POST":
<<<<<<< HEAD
        q_raw = request.form.get("search", "").strip()
        q_norm = normalize_medicine_query(q_raw)
        q_lower = q_raw.lower()
=======
        q = request.form.get("search", "").lower().strip()
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
        seen = set()
        if db:
            for d in db.collection("medicines").stream():
                item = d.to_dict()
                try:
                    ed = datetime.strptime(item.get("expiry", ""), "%Y-%m-%d").date()
                    if ed < date.today():
                        continue
                except Exception:
                    pass
<<<<<<< HEAD
                name = item.get("name", "")
                name_norm = normalize_medicine_query(name)
                name_lower = name.lower()
                pharm = item.get("pharmacy_email", "").lower()
                key = (name, pharm)
                # Case-insensitive + flexible: match "dolo-650", "DOLO650", "dolo 650" etc.
                if key not in seen and (q_lower in name_lower or (q_norm and q_norm in name_norm)):
                    seen.add(key)
                    # Add pharmacy lat/lon for "View Location" on same page
                    pid = item.get("pharmacy_email", "").replace("@", "_at_").replace(".", "_dot_")
                    pharm_doc = db.collection("pharmacies").document(pid).get()
                    if pharm_doc.exists:
                        p = pharm_doc.to_dict()
                        item["pharmacy_lat"] = p.get("lat")
                        item["pharmacy_lon"] = p.get("lon")
                        item["pharmacy_address"] = p.get("address", "")
                        item["pharmacy_name"] = p.get("pharmacy_name", item.get("pharmacy_email", ""))
                    item["doc_id"] = d.id
                    item["price"] = float(item.get("price") or 50)
=======
                name = item.get("name", "").lower()
                pharm = item.get("pharmacy_email", "").lower()
                key = (name, pharm)
                if q in name and key not in seen:
                    seen.add(key)
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
                    results.append(item)
        else:
            pharm_df, med_df = load_sample_data()
            for _, row in med_df.iterrows():
<<<<<<< HEAD
                name = str(row["medicine_name"])
                name_norm = normalize_medicine_query(name)
                name_lower = name.lower()
                pharm = str(row["pharmacy_email"]).lower()
                key = (name, pharm)
                if key not in seen and (q_lower in name_lower or (q_norm and q_norm in name_norm)):
                    seen.add(key)
                    rec = {
                        "name": row["medicine_name"],
                        "quantity": int(row["quantity"]),
                        "expiry": row["expiry_date"],
                        "pharmacy_email": row["pharmacy_email"],
                        "price": 50,
                        "doc_id": f"{row['medicine_name']}_{row['pharmacy_email']}".replace(" ", "_"),
                    }
                    prow = pharm_df[pharm_df["pharmacy_email"].astype(str).str.strip() == str(row["pharmacy_email"]).strip()]
                    if not prow.empty:
                        rec["pharmacy_lat"] = float(prow.iloc[0].get("lat", 17.3850))
                        rec["pharmacy_lon"] = float(prow.iloc[0].get("lon", 78.4867))
                        rec["pharmacy_address"] = prow.iloc[0].get("address", "")
                        rec["pharmacy_name"] = prow.iloc[0].get("pharmacy_name", row["pharmacy_email"])
                    results.append(rec)
    q_prefill = request.args.get("q", "").strip() if request.method == "GET" else request.form.get("search", "").strip()
    return render_template("user_search.html", results=results, searched_medicines=list({r.get("name") for r in results}), q_prefill=q_prefill)


# ---------------- USER MEDICINE INTEREST (Email Updates Opt-in) ----------------
@app.route("/user/interest", methods=["POST"])
@guest_allowed
def user_interest():
    """Save user interest for medicine updates (discounts, availability)."""

    # Handle both JSON requests and form submissions
    if request.is_json:
        data = request.get_json()
        email = (data.get("email") or "").strip()
        medicines = data.get("medicines", [])
        notify_discounts = data.get("notify_discounts", True)
    else:
        email = (request.form.get("email") or "").strip()
        medicines = request.form.getlist("medicines[]")
        notify_discounts = request.form.get("notify_discounts", "1") == "1"

    # ---------------- EMAIL VALIDATION ----------------
    if not email:
        return jsonify({"success": False, "error": "Email is required"}), 400

    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_pattern, email):
        return jsonify({"success": False, "error": "Please enter a valid email address"}), 400

    # ---------------- MEDICINE VALIDATION ----------------
    if not medicines or len(medicines) == 0:
        return jsonify({"success": False, "error": "Please select at least one medicine"}), 400

    # ---------------- SAVE DATA ----------------
    try:
        if db:
            for med_name in medicines:
                med_name = (med_name or "").strip()
                if not med_name:
                    continue

                doc_id = f"{email}_{med_name}".replace("@", "_at_").replace(".", "_dot_").replace(" ", "_")

                db.collection("user_medicine_interests").document(doc_id).set({
                    "email": email,
                    "medicine_name": med_name,
                    "notify_discounts": bool(notify_discounts),
                    "created_at": datetime.now().isoformat(),
                }, merge=True)

            return jsonify({
                "success": True,
                "message": "✅ Preferences saved! You will receive updates for selected medicines."
            })

        else:
            return jsonify({
                "success": True,
                "message": "Preferences saved (database not configured)."
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500
# ---------------- CART & ONLINE ORDERS ----------------
def get_cart():
    return session.get("cart") or []

def set_cart(cart):
    session["cart"] = cart
    session.modified = True

@app.route("/cart/add", methods=["POST"])
@guest_allowed
def cart_add():
    """Add medicine to cart. Requires: medicine_name, pharmacy_email, quantity, doc_id, unit_price, pharmacy_name."""
    medicine_name = request.form.get("medicine_name", "").strip()
    pharmacy_email = request.form.get("pharmacy_email", "").strip()
    try:
        qty = int(request.form.get("quantity", 1))
    except Exception:
        qty = 1
    doc_id = request.form.get("doc_id", "").strip()
    try:
        unit_price = float(request.form.get("unit_price", 50))
    except Exception:
        unit_price = 50
    pharmacy_name = request.form.get("pharmacy_name", pharmacy_email)
    if not medicine_name or not pharmacy_email or not doc_id:
        return jsonify({"success": False, "error": "Missing medicine details"}), 400
    if qty < 1:
        return jsonify({"success": False, "error": "Quantity must be at least 1"}), 400
    cart = get_cart()
    key = f"{doc_id}"
    found = False
    for i, c in enumerate(cart):
        if c.get("doc_id") == doc_id:
            cart[i]["quantity"] = cart[i].get("quantity", 0) + qty
            cart[i]["unit_price"] = unit_price
            found = True
            break
    if not found:
        cart.append({
            "medicine_name": medicine_name,
            "pharmacy_email": pharmacy_email,
            "pharmacy_name": pharmacy_name,
            "quantity": qty,
            "doc_id": doc_id,
            "unit_price": unit_price,
        })
    set_cart(cart)
    if request.accept_mimetypes.best == "text/html" or "application/json" not in request.accept_mimetypes:
        return redirect(url_for("cart_page"))
    return jsonify({"success": True, "message": f"Added {medicine_name} to cart", "cart_count": sum(c.get("quantity", 0) for c in cart)})

@app.route("/cart/update", methods=["POST"])
@guest_allowed
def cart_update():
    doc_id = request.form.get("doc_id", "").strip()
    try:
        qty = int(request.form.get("quantity", 0))
    except Exception:
        qty = 0
    cart = get_cart()
    if qty <= 0:
        cart = [c for c in cart if c.get("doc_id") != doc_id]
    else:
        for c in cart:
            if c.get("doc_id") == doc_id:
                c["quantity"] = qty
                break
    set_cart(cart)
    return redirect(url_for("cart_page"))

@app.route("/cart/remove", methods=["POST"])
@guest_allowed
def cart_remove():
    doc_id = request.form.get("doc_id", "").strip()
    cart = [c for c in get_cart() if c.get("doc_id") != doc_id]
    set_cart(cart)
    return redirect(url_for("cart_page"))

@app.route("/cart")
@guest_allowed
def cart_page():
    cart = get_cart()
    total = sum((c.get("unit_price", 0) * c.get("quantity", 0)) for c in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "GET":
        cart = get_cart()
        if not cart:
            return redirect(url_for("user_search"))
        if not session.get("user_email"):
            return redirect(url_for("login", role="user", next=url_for("checkout")))
        total = sum((c.get("unit_price", 0) * c.get("quantity", 0)) for c in cart)
        return render_template("checkout.html", cart=cart, total=total)
    # POST - place order
    if not session.get("user_email"):
        return redirect(url_for("login", role="user"))
    cart = get_cart()
    if not cart:
        return jsonify({"success": False, "error": "Cart is empty"}), 400
    delivery_address = request.form.get("delivery_address", "").strip()
    phone = request.form.get("phone", "").strip() or (session.get("user_phone") or "")
    if not delivery_address:
        return jsonify({"success": False, "error": "Delivery address is required"}), 400
    user_email = session.get("user_email")
    user_name = session.get("user_name") or user_email.split("@")[0]
    if not db:
        set_cart([])
        return redirect(url_for("user_orders", message="Order placed (demo mode)"))
    from firebase_admin import firestore as _fs
    orders_created = []
    by_pharmacy = {}
    for c in cart:
        ph = c.get("pharmacy_email", "")
        if ph not in by_pharmacy:
            by_pharmacy[ph] = []
        by_pharmacy[ph].append(c)
    for pharmacy_email, items in by_pharmacy.items():
        order_total = sum(i.get("unit_price", 0) * i.get("quantity", 0) for i in items)
        order_items = [{"medicine_name": i["medicine_name"], "quantity": i["quantity"], "unit_price": i["unit_price"], "doc_id": i.get("doc_id"), "total": i["unit_price"] * i["quantity"]} for i in items]
        order_data = {
            "user_email": user_email,
            "user_name": user_name,
            "user_phone": phone,
            "pharmacy_email": pharmacy_email,
            "items": order_items,
            "total_amount": order_total,
            "delivery_address": delivery_address,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        ref = db.collection("orders").add(order_data)
        orders_created.append(ref[1].id)
    set_cart([])
    return redirect(url_for("user_orders", message="Order placed successfully"))

@app.route("/orders")
@login_required(role="user")
def user_orders():
    message = request.args.get("message", "")
    orders_list = []
    if db:
        for d in db.collection("orders").where("user_email", "==", session.get("user_email")).stream():
            o = d.to_dict()
            o["order_id"] = d.id
            orders_list.append(o)
        orders_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return render_template("user_orders.html", orders=orders_list, message=message)

@app.route("/pharmacy/orders")
@login_required(role="pharmacy")
def pharmacy_orders():
    pharmacy_email = session.get("user_email")
    orders_list = []
    if db:
        for d in db.collection("orders").where("pharmacy_email", "==", pharmacy_email).stream():
            o = d.to_dict()
            o["order_id"] = d.id
            orders_list.append(o)
        orders_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return render_template("pharmacy_orders.html", orders=orders_list)

@app.route("/pharmacy/order/status", methods=["POST"])
@login_required(role="pharmacy")
def pharmacy_order_status():
    order_id = request.form.get("order_id", "").strip()
    new_status = request.form.get("status", "").strip()
    if not order_id or new_status not in ("confirmed", "ready", "out_for_delivery", "delivered", "cancelled"):
        return redirect(url_for("pharmacy_orders"))
    if not db:
        return redirect(url_for("pharmacy_orders"))
    pharmacy_email = session.get("user_email")
    doc = db.collection("orders").document(order_id).get()
    if not doc.exists or doc.to_dict().get("pharmacy_email") != pharmacy_email:
        return redirect(url_for("pharmacy_orders"))
    db.collection("orders").document(order_id).update({
        "status": new_status,
        "updated_at": datetime.now().isoformat(),
    })
    if new_status == "delivered":
        for item in doc.to_dict().get("items", []):
            doc_id = item.get("doc_id")
            qty_sold = item.get("quantity", 0)
            if doc_id and db:
                med_doc = db.collection("medicines").document(doc_id).get()
                if med_doc.exists:
                    med = med_doc.to_dict()
                    if med.get("pharmacy_email") == pharmacy_email:
                        current = int(med.get("quantity", 0))
                        db.collection("medicines").document(doc_id).update({"quantity": max(0, current - qty_sold)})
    return redirect(url_for("pharmacy_orders"))

=======
                name = str(row["medicine_name"]).lower()
                pharm = str(row["pharmacy_email"]).lower()
                key = (name, pharm)
                if q in name and key not in seen:
                    seen.add(key)
                    results.append(
                        {
                            "name": row["medicine_name"],
                            "quantity": int(row["quantity"]),
                            "expiry": row["expiry_date"],
                            "pharmacy_email": row["pharmacy_email"],
                        }
                    )
    return render_template("user_search.html", results=results)
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54

# ---------------- PHARMACIES API (for map) ---------------- 
@app.route("/pharmacies_api")
def pharmacies_api():
<<<<<<< HEAD
    q_raw = request.args.get("q", "").strip()
    q_lower = q_raw.lower()
    q_norm = normalize_medicine_query(q_raw)
=======
    q = request.args.get("q", "").lower().strip()
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
    try:
        user_lat = float(request.args.get("lat", 17.3850))
        user_lon = float(request.args.get("lon", 78.4867))
    except Exception:
        return jsonify({"error": "Invalid lat/lon parameters"}), 400

    radius_km = float(request.args.get("radius", 15))
    results = []

    try:
        if db:
            pharm_docs = {d.id: d.to_dict() for d in db.collection("pharmacies").stream()}
            for med_doc in db.collection("medicines").stream():
                med = med_doc.to_dict()
<<<<<<< HEAD
                name = str(med.get("name", ""))
                name_lower = name.lower()
                name_norm = normalize_medicine_query(name)
                if q_raw and q_lower not in name_lower and (not q_norm or q_norm not in name_norm):
=======
                name = str(med.get("name", "")).lower()
                if q and q not in name:
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
                    continue
                email = med.get("pharmacy_email", "").strip()
                if not email:
                    continue
                pid = email.replace("@", "_at_").replace(".", "_dot_")
                pharm = pharm_docs.get(pid)
                if not pharm:
                    continue
                try:
                    lat = float(pharm.get("lat"))
                    lon = float(pharm.get("lon"))
                except Exception:
                    continue
                dist = haversine(user_lat, user_lon, lat, lon)
                if dist <= radius_km:
<<<<<<< HEAD
                    unit_price = float(med.get("price") or 50)
                    effective_price, _ = apply_discount(unit_price, med)
=======
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
                    results.append(
                        {
                            "name": med.get("name"),
                            "quantity": med.get("quantity"),
                            "expiry": med.get("expiry"),
                            "pharmacy_email": email,
                            "pharmacy_name": pharm.get("pharmacy_name", ""),
                            "lat": lat,
                            "lon": lon,
                            "address": pharm.get("address", ""),
                            "distance": round(dist, 2),
<<<<<<< HEAD
                            "doc_id": med_doc.id,
                            "price": effective_price,
=======
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
                        }
                    )
        else:
            pharm_df, med_df = load_sample_data()
            med_df["pharmacy_email"] = med_df["pharmacy_email"].astype(str).str.strip()
            pharm_df["pharmacy_email"] = pharm_df["pharmacy_email"].astype(str).str.strip()
            for _, row in med_df.iterrows():
<<<<<<< HEAD
                name = str(row.get("medicine_name", ""))
                name_lower = name.lower()
                name_norm = normalize_medicine_query(name)
                if q_raw and q_lower not in name_lower and (not q_norm or q_norm not in name_norm):
=======
                name = str(row.get("medicine_name", "")).lower()
                if q and q not in name:
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
                    continue
                email = row.get("pharmacy_email", "")
                prow = pharm_df[pharm_df["pharmacy_email"] == email]
                if prow.empty:
                    continue
                lat = float(prow.iloc[0]["lat"])
                lon = float(prow.iloc[0]["lon"])
                dist = haversine(user_lat, user_lon, lat, lon)
                if dist <= radius_km:
<<<<<<< HEAD
                    doc_id = f"{row.get('medicine_name','')}_{row.get('batch_no','')}_{email}".replace(" ", "_").replace("__", "_").strip("_") or f"{row.get('medicine_name','')}_{email}".replace(" ", "_")
=======
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
                    results.append(
                        {
                            "name": row.get("medicine_name"),
                            "quantity": int(row.get("quantity", 0)),
                            "expiry": row.get("expiry_date") or row.get("expiry"),
                            "pharmacy_email": email,
                            "pharmacy_name": prow.iloc[0].get("pharmacy_name", ""),
                            "lat": lat,
                            "lon": lon,
                            "address": prow.iloc[0].get("address", ""),
                            "distance": round(dist, 2),
<<<<<<< HEAD
                            "doc_id": doc_id,
                            "price": 50,
=======
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
                        }
                    )

        results.sort(key=lambda x: x.get("distance", 9999))
        return jsonify(results)
    except Exception as e:
        print("Error in pharmacies_api:", e)
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# ---------------- BILLING ---------------- 
@app.route("/billing", methods=["GET", "POST"])
@login_required(role="pharmacy")
def billing():
    message = ""
    pharmacy_email = session.get("user_email")
    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip() or "Walk-in Customer"
        medicine_names = request.form.getlist("medicine_name[]")
        quantities = request.form.getlist("quantity[]")

        billed_items = []
        total_amount = 0
        errors = []

        for i, name_query in enumerate(medicine_names):
            name_query = name_query.strip().lower()
            qty_to_sell = int(quantities[i]) if i < len(quantities) and quantities[i] else 1

            found = False
            med = None
            doc_id = None
            if db:
                # Search only in logged-in pharmacy medicines
                for d in db.collection("medicines").where("pharmacy_email", "==", pharmacy_email).stream():
                    item = d.to_dict()
                    if name_query in item.get("name", "").lower():
                        med = item
                        doc_id = d.id
                        found = True
                        break
            else:
                _, med_df = load_sample_data()
                rows = med_df[(med_df["medicine_name"].str.lower().str.contains(name_query, na=False)) & 
                             (med_df["pharmacy_email"] == pharmacy_email)]
                if not rows.empty:
                    row = rows.iloc[0]
                    med = {"name": row["medicine_name"], "quantity": int(row["quantity"]), "expiry": row["expiry_date"], "pharmacy_email": row["pharmacy_email"]}
                    found = True

            if not found:
                errors.append(f"❌ '{name_query}' not found in your inventory.")
                continue

            expiry_value = (med.get("expiry") or med.get("expiry_date") or "").strip()
            if not expiry_value:
                errors.append(f"⚠️ '{med.get('name')}' has no expiry date set. Please update pharmacy data.")
                continue

            try:
                expiry_date = datetime.strptime(expiry_value, "%Y-%m-%d").date()
            except ValueError:
                errors.append(f"⚠️ Invalid expiry format for '{med.get('name')}'.")
                continue

            if expiry_date < date.today():
                if db:
                    db.collection("violations").add(
                        {"pharmacy_email": med.get("pharmacy_email"), "medicine_name": med.get("name"), "attempted_on": datetime.now().isoformat(), "reason": "Attempted to sell expired medicine"}
                    )
                errors.append(f"❌ '{med.get('name')}' expired on {expiry_value}.")
                continue

            current_qty = int(med.get("quantity", 0))
            if current_qty < qty_to_sell:
                errors.append(f"⚠️ Only {current_qty} left for '{med.get('name')}'.")
                continue

            new_qty = current_qty - qty_to_sell
            if db and doc_id:
                db.collection("medicines").document(doc_id).update({"quantity": new_qty})
                try:
                    import blockchain_audit
                    blockchain_audit.log_inventory_change(
                        pharmacy_email, doc_id, "quantity_change",
                        before={"quantity": current_qty},
                        after={"quantity": new_qty},
                        extra={"quantity_sold": qty_to_sell, "billing": True},
                    )
                except Exception:
                    pass
            else:
                med_df = pd.read_csv("sample_csvs/erp_bulk_medicines.csv")
                idx = med_df[(med_df["medicine_name"].str.lower().str.contains(name_query, na=False)) & 
                            (med_df["pharmacy_email"] == pharmacy_email)].index
                if not idx.empty:
                    iidx = idx[0]
                    med_df.at[iidx, "quantity"] = max(0, new_qty)
                    med_df.to_csv("sample_csvs/erp_bulk_medicines.csv", index=False)

            price_per_unit = med.get("price", 50) or 50
            effective_price, discount_applied = apply_discount(price_per_unit, med)
            total_price = qty_to_sell * effective_price
            total_amount += total_price

            billed_items.append({
                "medicine": med.get("name"),
                "qty": qty_to_sell,
                "price": effective_price,
                "total": total_price,
                "discount_applied": discount_applied,
            })

            if db:
                db.collection("bills").add(
                    {"customer_name": customer_name, "medicine_name": med.get("name"), "quantity_sold": qty_to_sell, "price_per_unit": price_per_unit, "total_price": total_price, "sold_at": datetime.now().isoformat(), "pharmacy_email": med.get("pharmacy_email")}
                )

        if billed_items:
            os.makedirs("static/bills", exist_ok=True)
            bill_filename = f"bill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            bill_path = os.path.join("static", "bills", bill_filename)

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, txt="MedScope Pharmacy Bill", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.cell(200, 10, txt=f"Customer: {customer_name}", ln=True)
            pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
            pdf.ln(8)

            pdf.set_font("Arial", "B", 12)
            pdf.cell(60, 10, "Medicine", 1)
            pdf.cell(30, 10, "Qty", 1)
            pdf.cell(40, 10, "Price", 1)
            pdf.cell(50, 10, "Total", 1, ln=True)
            pdf.set_font("Arial", "", 12)
            for item in billed_items:
                pdf.cell(60, 10, item["medicine"][:30], 1)
                pdf.cell(30, 10, str(item["qty"]), 1)
                pdf.cell(40, 10, f"Rs.{item['price']}", 1)
                pdf.cell(50, 10, f"Rs.{item['total']}", 1, ln=True)

            pdf.set_font("Arial", "B", 12)
            pdf.cell(130, 10, "Grand Total", 1)
            pdf.cell(50, 10, f"Rs.{total_amount}", 1, ln=True)
            pdf.output(bill_path)

            return render_template("bill_preview.html", pdf_url=url_for("static", filename=f"bills/{bill_filename}"), total_amount=total_amount, customer_name=customer_name, date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        message = "\n".join(errors) if errors else "⚠️ No valid medicines billed."
    return render_template("billing.html", message=message)

# ---------------- QUICK SELL (Prevents Expired Medicine Sale) ---------------- 
@app.route("/quick_sell", methods=["POST"])
@login_required(role="pharmacy")
def quick_sell():
    """Quick sell medicine with expiry validation - for shops without billing system"""
    pharmacy_email = session.get("user_email")
    medicine_name = request.form.get("medicine_name", "").strip()
    quantity_sold = int(request.form.get("quantity", 1))
    doc_id = request.form.get("doc_id", "").strip()
    
    if not medicine_name or not doc_id:
        return jsonify({"success": False, "error": "Missing medicine information"}), 400
    
    try:
        if db:
            # Get medicine details
            med_doc = db.collection("medicines").document(doc_id).get()
            if not med_doc.exists:
                return jsonify({"success": False, "error": "Medicine not found"}), 404
            
            med = med_doc.to_dict()
            
            # Verify it belongs to logged-in pharmacy
            if med.get("pharmacy_email") != pharmacy_email:
                return jsonify({"success": False, "error": "Unauthorized"}), 403
            
            # Check if expired
            expiry_str = med.get("expiry", "")
            if expiry_str:
                try:
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                    if expiry_date < date.today():
                        # Log violation
                        db.collection("violations").add({
                            "pharmacy_email": pharmacy_email,
                            "medicine_name": medicine_name,
                            "attempted_on": datetime.now().isoformat(),
                            "reason": "Attempted to sell expired medicine via Quick Sell",
                            "quantity_attempted": quantity_sold
                        })
                        return jsonify({
                            "success": False, 
                            "error": f"❌ CANNOT SELL: {medicine_name} expired on {expiry_str}. Please remove from stock."
                        }), 400
                except ValueError:
                    pass
            
            # Check quantity
            current_qty = int(med.get("quantity", 0))
            if current_qty < quantity_sold:
                return jsonify({
                    "success": False, 
                    "error": f"Only {current_qty} units available"
                }), 400
            
            # Update quantity
            new_qty = current_qty - quantity_sold
            db.collection("medicines").document(doc_id).update({"quantity": new_qty})
            try:
                import blockchain_audit
                blockchain_audit.log_inventory_change(
                    pharmacy_email, doc_id, "quantity_change",
                    before={"quantity": current_qty},
                    after={"quantity": new_qty},
                    extra={"quantity_sold": quantity_sold},
                )
            except Exception:
                pass
            # Log sale
            db.collection("sales").add({
                "pharmacy_email": pharmacy_email,
                "medicine_name": medicine_name,
                "quantity_sold": quantity_sold,
                "sold_at": datetime.now().isoformat(),
                "method": "quick_sell"
            })
            
            return jsonify({
                "success": True, 
                "message": f"✅ Sold {quantity_sold} unit(s) of {medicine_name}. Remaining: {new_qty}"
            })
        else:
            return jsonify({"success": False, "error": "Database not available"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ---------------- REMOVE EXPIRED STOCK ---------------- 
@app.route("/remove_expired", methods=["POST"])
@login_required(role="pharmacy")
def remove_expired():
    """Remove expired medicines from stock"""
    pharmacy_email = session.get("user_email")
    doc_id = request.form.get("doc_id", "").strip()
    
    if not doc_id:
        return jsonify({"success": False, "error": "Missing medicine ID"}), 400
    
    try:
        if db:
            med_doc = db.collection("medicines").document(doc_id).get()
            if not med_doc.exists:
                return jsonify({"success": False, "error": "Medicine not found"}), 404
            
            med = med_doc.to_dict()
            
            # Verify it belongs to logged-in pharmacy
            if med.get("pharmacy_email") != pharmacy_email:
                return jsonify({"success": False, "error": "Unauthorized"}), 403
            
            # Verify it's actually expired
            expiry_str = med.get("expiry", "")
            is_expired = False
            if expiry_str:
                try:
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                    if expiry_date < date.today():
                        is_expired = True
                except ValueError:
                    pass
            
            if not is_expired:
                return jsonify({
                    "success": False, 
                    "error": "Medicine is not expired. Only expired medicines can be removed."
                }), 400
            
            # Delete medicine
            db.collection("medicines").document(doc_id).delete()
            try:
                import blockchain_audit
                blockchain_audit.log_inventory_change(
                    pharmacy_email, doc_id, "remove",
                    before=med, after=None,
                )
            except Exception:
                pass
            # Log removal
            db.collection("expired_removals").add({
                "pharmacy_email": pharmacy_email,
                "medicine_name": med.get("name"),
                "expiry_date": expiry_str,
                "quantity_removed": med.get("quantity", 0),
                "removed_at": datetime.now().isoformat()
            })
            
            return jsonify({
                "success": True, 
                "message": f"✅ Removed expired {med.get('name')} from stock"
            })
        else:
            return jsonify({"success": False, "error": "Database not available"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------- DISCOUNT MANAGEMENT (PHARMACY) ---------------- 
@app.route("/pharmacy/discount/set", methods=["POST"])
@login_required(role="pharmacy")
def pharmacy_discount_set():
    """Set or update discount for a medicine (pharmacy-owned only)."""
    pharmacy_email = session.get("user_email")
    doc_id = request.form.get("doc_id", "").strip()
    discount_value = request.form.get("discount_value", "").strip()
    discount_type = (request.form.get("discount_type") or "percentage").strip().lower()
    discount_valid_till = request.form.get("discount_valid_till", "").strip()

    if not doc_id:
        return jsonify({"success": False, "error": "Missing medicine ID"}), 400
    if discount_type not in ("percentage", "flat"):
        discount_type = "percentage"
    try:
        val = float(discount_value)
        if val < 0 or (discount_type == "percentage" and val > 100):
            return jsonify({"success": False, "error": "Invalid discount value"}), 400
    except ValueError:
        return jsonify({"success": False, "error": "Discount value must be a number"}), 400
    try:
        datetime.strptime(discount_valid_till, "%Y-%m-%d")
    except ValueError:
        return jsonify({"success": False, "error": "Valid till date must be YYYY-MM-DD"}), 400

    if not db:
        return jsonify({"success": False, "error": "Database not available"}), 500

    med_doc = db.collection("medicines").document(doc_id).get()
    if not med_doc.exists:
        return jsonify({"success": False, "error": "Medicine not found"}), 404
    med = med_doc.to_dict()
    if med.get("pharmacy_email") != pharmacy_email:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    before_discount = {
        k: med.get(k) for k in ("discount_value", "discount_type", "discount_valid_till")
    }
    db.collection("medicines").document(doc_id).update({
        "discount_value": val,
        "discount_type": discount_type,
        "discount_valid_till": discount_valid_till,
    })
<<<<<<< HEAD
    send_discount_alerts(med.get("name"), val, discount_type, discount_valid_till)
=======
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
    after_discount = {"discount_value": val, "discount_type": discount_type, "discount_valid_till": discount_valid_till}
    try:
        import blockchain_audit
        blockchain_audit.log_discount_change(
            pharmacy_email, doc_id, "set",
            before=before_discount, after=after_discount,
        )
    except Exception:
        pass
    return jsonify({
        "success": True,
        "message": f"Discount set for {med.get('name')} (valid till {discount_valid_till})",
    })


<<<<<<< HEAD





=======
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
@app.route("/pharmacy/discount/remove", methods=["POST"])
@login_required(role="pharmacy")
def pharmacy_discount_remove():
    """Remove discount for a medicine (pharmacy-owned only)."""
    pharmacy_email = session.get("user_email")
    doc_id = request.form.get("doc_id", "").strip()

    if not doc_id:
        return jsonify({"success": False, "error": "Missing medicine ID"}), 400
    if not db:
        return jsonify({"success": False, "error": "Database not available"}), 500

    med_doc = db.collection("medicines").document(doc_id).get()
    if not med_doc.exists:
        return jsonify({"success": False, "error": "Medicine not found"}), 404
    med = med_doc.to_dict()
    if med.get("pharmacy_email") != pharmacy_email:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    before_discount = {
        k: med.get(k) for k in ("discount_value", "discount_type", "discount_valid_till")
    }
    from firebase_admin import firestore as _fs
    db.collection("medicines").document(doc_id).update({
        "discount_value": _fs.DELETE_FIELD,
        "discount_type": _fs.DELETE_FIELD,
        "discount_valid_till": _fs.DELETE_FIELD,
    })
    try:
        import blockchain_audit
        blockchain_audit.log_discount_change(
            pharmacy_email, doc_id, "remove",
            before=before_discount, after=None,
        )
    except Exception:
        pass
    return jsonify({
        "success": True,
        "message": f"Discount removed for {med.get('name')}",
    })


# ---------------- DEMAND FORECASTING ---------------- 
@app.route("/pharmacy/forecast")
@login_required(role="pharmacy")
def pharmacy_forecast():
    """Return demand forecast for logged-in pharmacy (next 30 days, basic average-based)."""
    pharmacy_email = session.get("user_email")
    if not db:
        return jsonify({"forecasts": [], "error": "Database not available"})
    try:
        import forecasting
        forecasts = forecasting.forecast_demand(db, pharmacy_email, horizon_days=30, history_days=60)
        return jsonify({"forecasts": forecasts})
    except Exception as e:
        print("Forecast error:", e)
        return jsonify({"forecasts": [], "error": str(e)})


# ---------------- MAP PAGE ---------------- 
@app.route("/map")
def map_page():
    return render_template("map.html")

# ---------------- ADMIN DASHBOARD ---------------- 
@app.route("/admin")
@login_required(role="admin")
def admin():
    meds = []
    counts = {"Available": 0, "Expiring Soon": 0, "Expired": 0}
    alerts = []
    pending_pharmacies = []
    violations_list = []
<<<<<<< HEAD
    orders_list = []
=======
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54

    if db:
        for d in db.collection("medicines").stream():
            i = d.to_dict()
            i["status"] = get_status(i.get("expiry") or i.get("expiry_date"))
            if i["status"] in counts:
                counts[i["status"]] += 1
            meds.append(i)

        for a in db.collection("alerts").order_by("sent_on", direction="DESCENDING").limit(20).stream():
            alerts.append(a.to_dict())

        for d in db.collection("pharmacies").stream():
            data = d.to_dict()
            if (data.get("pharmacy_status") or "approved") == "pending":
                data["pid"] = d.id
                pending_pharmacies.append(data)

<<<<<<< HEAD
        try:
            _DESC = 2  # Firestore DESCENDING
            for v in db.collection("violations").order_by("attempted_on", direction=_DESC).limit(100).stream():
                violations_list.append(v.to_dict())
        except Exception:
            for v in db.collection("violations").limit(100).stream():
                violations_list.append(v.to_dict())
            violations_list.sort(key=lambda x: (x.get("attempted_on") or ""), reverse=True)
        for d in db.collection("orders").stream():
            o = d.to_dict()
            o["order_id"] = d.id
            orders_list.append(o)
        orders_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
=======
        for v in db.collection("violations").limit(100).stream():
            violations_list.append(v.to_dict())
        violations_list.sort(key=lambda x: (x.get("attempted_on") or ""), reverse=True)
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
    else:
        pharm_df, med_df = load_sample_data()
        for _, row in med_df.iterrows():
            st = get_status(row["expiry_date"])
            meds.append({"name": row["medicine_name"], "quantity": int(row["quantity"]), "expiry": row["expiry_date"], "pharmacy_email": row["pharmacy_email"], "status": st})
            counts[st] = counts.get(st, 0) + 1

<<<<<<< HEAD
    return render_template("admin_dashboard.html", medicines=meds, counts=counts, alerts=alerts, pending_pharmacies=pending_pharmacies, violations=violations_list, orders_list=orders_list)
=======
    return render_template("admin_dashboard.html", medicines=meds, counts=counts, alerts=alerts, pending_pharmacies=pending_pharmacies, violations=violations_list)
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54


@app.route("/admin/approve_pharmacy", methods=["POST"])
@login_required(role="admin")
def approve_pharmacy():
    pid = (request.form.get("pid") or request.form.get("pharmacy_id") or "").strip()
    if not pid and db:
        return redirect(url_for("admin"))
    if db:
        db.collection("pharmacies").document(pid).set({"pharmacy_status": "approved"}, merge=True)
    return redirect(url_for("admin"))


@app.route("/admin/reject_pharmacy", methods=["POST"])
@login_required(role="admin")
def reject_pharmacy():
    pid = (request.form.get("pid") or request.form.get("pharmacy_id") or "").strip()
    if not pid and db:
        return redirect(url_for("admin"))
    if db:
        db.collection("pharmacies").document(pid).set({"pharmacy_status": "rejected"}, merge=True)
    return redirect(url_for("admin"))


@app.route("/admin/verify_audit", methods=["GET", "POST"])
@login_required(role="admin")
def verify_audit():
    """Verify audit chain integrity. If tampering detected, log to violations."""
    try:
        import blockchain_audit
        valid, broken_index = blockchain_audit.verify_chain()
        if not valid and db is not None:
            db.collection("violations").add({
                "pharmacy_email": "(system)",
                "medicine_name": "(audit chain)",
                "attempted_on": datetime.now().isoformat(),
                "reason": f"Audit chain tampering detected at block_{broken_index}. Invoice/expiry data may have been altered.",
            })
        return jsonify({"valid": valid, "broken_index": broken_index})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500


@app.route("/export_medicines_csv")
@login_required(role="admin")
def export_medicines_csv():
    """Export all medicines (name, quantity, expiry, pharmacy, status) as a CSV file for backup or analysis."""
    rows = []
    if db:
        for d in db.collection("medicines").stream():
            i = d.to_dict()
            i["status"] = get_status(i.get("expiry") or i.get("expiry_date"))
            rows.append({
                "name": i.get("name", ""),
                "quantity": i.get("quantity", 0),
                "expiry": i.get("expiry") or i.get("expiry_date", ""),
                "pharmacy_email": i.get("pharmacy_email", ""),
                "status": i.get("status", ""),
            })
    else:
        _, med_df = load_sample_data()
        for _, row in med_df.iterrows():
            st = get_status(row["expiry_date"])
            rows.append({
                "name": row.get("medicine_name", ""),
                "quantity": int(row.get("quantity", 0)),
                "expiry": row.get("expiry_date", ""),
                "pharmacy_email": row.get("pharmacy_email", ""),
                "status": st,
            })
    df = pd.DataFrame(rows)
    from io import StringIO
    buf = StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return Response(
        buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=medicines_export.csv"},
    )


@app.route("/admin/send_alerts_now", methods=["GET", "POST"])
@login_required(role="admin")
def admin_send_alerts_now():
    """Trigger expiry alerts immediately (for testing email delivery)."""
    send_expiry_alerts()
    return redirect(url_for("admin"))


# ---------------- ALERTS JOB ---------------- 
def send_expiry_alerts():
    """Send expiry alerts for expired and expiring soon medicines"""
    print("⏰ Running expiry alert job...")
    if not db:
        print("⚠️ Firestore not configured; skipping alerts.")
        return

    today = date.today()
    sent = 0
    try:
        for d in db.collection("medicines").stream():
            med = d.to_dict()
            expiry_str = med.get("expiry") or med.get("expiry_date")
            if not expiry_str:
                continue
            try:
                ed = datetime.strptime(expiry_str, "%Y-%m-%d").date()
            except Exception:
                continue
            
            days_left = (ed - today).days
            
            # Alert for expired medicines (days_left < 0)
            if days_left < 0:
                subject = f"🚨 URGENT: Medicine Expired - {med.get('name')}"
                body = f"Dear Pharmacy,\n\nURGENT: Your stock '{med.get('name')}' (qty: {med.get('quantity')}) has EXPIRED on {expiry_str} ({abs(days_left)} days ago).\n\nPlease remove from inventory immediately.\n\nRegards,\nMedScope"
                
                pharmacy_email = med.get("pharmacy_email")
                # Get pharmacy phone if available
                pharmacy_phone = None
                if pharmacy_email:
                    pid = pharmacy_email.replace("@", "_at_").replace(".", "_dot_")
                    pharm_doc = db.collection("pharmacies").document(pid).get()
                    if pharm_doc.exists:
                        pharmacy_phone = pharm_doc.to_dict().get("phone")
                
                email_ok = send_email(pharmacy_email, subject, body, cc=ADMIN_EMAIL if ADMIN_EMAIL else None)
                if pharmacy_phone:
                    send_sms(pharmacy_phone, f"URGENT: {med.get('name')} expired {abs(days_left)} days ago. Remove from inventory.")
                
                db.collection("alerts").add({
                    "medicine_name": med.get("name"),
                    "pharmacy_email": pharmacy_email,
                    "expiry_date": expiry_str,
                    "days_left": days_left,
                    "sent_on": datetime.now().isoformat(),
                    "status": "Sent" if email_ok else "Failed",
                    "alert_type": "Expired"
                })
                if email_ok:
                    sent += 1
            
            # Alert for expiring soon (0 <= days_left <= 30)
            elif 0 <= days_left <= 30:
                subject = f"⚠️ Expiry Alert: {med.get('name')} expires in {days_left} days"
                body = f"Dear Pharmacy,\n\nYour stock '{med.get('name')}' (qty: {med.get('quantity')}) will expire on {expiry_str} ({days_left} days left).\n\nPlease take necessary action.\n\nRegards,\nMedScope"
                
                pharmacy_email = med.get("pharmacy_email")
                pharmacy_phone = None
                if pharmacy_email:
                    pid = pharmacy_email.replace("@", "_at_").replace(".", "_dot_")
                    pharm_doc = db.collection("pharmacies").document(pid).get()
                    if pharm_doc.exists:
                        pharmacy_phone = pharm_doc.to_dict().get("phone")
                
                email_ok = send_email(pharmacy_email, subject, body, cc=ADMIN_EMAIL if ADMIN_EMAIL else None)
                if pharmacy_phone:
                    send_sms(pharmacy_phone, f"Alert: {med.get('name')} expires in {days_left} days on {expiry_str}.")
                
                db.collection("alerts").add({
                    "medicine_name": med.get("name"),
                    "pharmacy_email": pharmacy_email,
                    "expiry_date": expiry_str,
                    "days_left": days_left,
                    "sent_on": datetime.now().isoformat(),
                    "status": "Sent" if email_ok else "Failed",
                    "alert_type": "Expiring Soon"
                })
                if email_ok:
                    sent += 1
        
        print(f"✅ Alerts job completed. Emails sent: {sent}")
    except Exception as e:
        print("❌ Error in alerts job:", e)

<<<<<<< HEAD
# ---------------- AUTO REMOVE EXPIRED DISCOUNTS ---------------- 
def remove_expired_discounts():
    """Remove discounts whose discount_valid_till has passed - run daily."""
    if not db:
        return
    today = date.today()
    removed = 0
    try:
        from firebase_admin import firestore as _fs
        for d in db.collection("medicines").stream():
            med = d.to_dict()
            valid_till = (med.get("discount_valid_till") or "").strip()
            if not valid_till:
                continue
            try:
                valid_date = datetime.strptime(valid_till[:10], "%Y-%m-%d").date()
            except Exception:
                continue
            if valid_date < today:
                db.collection("medicines").document(d.id).update({
                    "discount_value": _fs.DELETE_FIELD,
                    "discount_type": _fs.DELETE_FIELD,
                    "discount_valid_till": _fs.DELETE_FIELD,
                })
                removed += 1
        if removed:
            print(f"✅ Auto-removed {removed} expired discount(s)")
    except Exception as e:
        print("⚠️ Auto discount removal error:", e)


# ---------------- SCHEDULER ----------------
def start_scheduler():
    """Start APScheduler once (avoid duplicate schedulers in debug/reloader)."""
    sched = BackgroundScheduler()
    sched.add_job(send_expiry_alerts, "cron", hour=9, minute=0)  # daily 9 AM
    sched.add_job(remove_expired_discounts, "cron", hour=0, minute=5)  # daily 00:05
    sched.start()
    atexit.register(lambda: sched.shutdown())
    return sched

_scheduler = None


@app.route("/admin/run_discount_cleanup", methods=["POST"])
@login_required(role="admin")
def admin_run_discount_cleanup():
    """Manually trigger discount cleanup (for testing)."""
    remove_expired_discounts()
    return redirect(url_for("admin"))
=======
# ---------------- SCHEDULER ---------------- 
scheduler = BackgroundScheduler()
scheduler.add_job(send_expiry_alerts, "cron", hour=9, minute=0)  # Run daily at 9 AM
scheduler.start()
atexit.register(lambda: scheduler.shutdown())
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54

# ---------------- MAIN ---------------- 
if __name__ == "__main__":
    # ensure folders exist
    os.makedirs("static/bills", exist_ok=True)
<<<<<<< HEAD
    # Start scheduler only once. In debug mode, disable reloader to prevent duplicate schedulers.
    _scheduler = start_scheduler()
    app.run(debug=True, use_reloader=False)
=======
    app.run(debug=True)
>>>>>>> 288cb523e87be41f6926f23d221a67c467592a54
