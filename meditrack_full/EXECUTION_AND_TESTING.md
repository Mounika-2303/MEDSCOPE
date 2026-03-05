# Step-by-Step Execution and Testing Guide

Follow this guide to run the app and verify each feature.

---

## Prerequisites

1. **Python** (3.8+) and **pip** installed.
2. **`.env`** file in the project root with:
   - `GMAIL_SENDER` = your Gmail
   - `GMAIL_APP_PASSWORD` = Gmail App Password (see EMAIL_SETUP.md)
   - `ADMIN_EMAIL` = optional
3. **Firebase**: `serviceAccountKey.json` in the project root (for Firestore).

---

## 1. Start the application

```powershell
cd c:\Users\MOUNIKA\Desktop\cursor\meditrack_full
.\venv\Scripts\activate
python app.py
```

You should see:
- `✅ Firestore initialized.`
- `✅ Blockchain audit logging enabled.`
- `* Running on http://127.0.0.1:5000`

Open **http://localhost:5000** in your browser.

---

## 2. Test Pharmacy Dashboard – Discount button

**Goal:** Pharmacy can set/edit/remove discount per medicine.

1. Log in as **Pharmacy** (register one at `/register?role=pharmacy` if needed).
2. Go to **Pharmacy Dashboard**.
3. Ensure you have at least one medicine in the table (add via “Add one medicine manually” or load an invoice CSV).
4. In the **Actions** column, click the **🏷️ Discount** button on any row.
5. **Expected:** A modal opens titled “Set / Edit Discount” with:
   - Medicine name
   - Discount type (Percentage / Flat)
   - Discount value
   - Valid till (date)
6. Fill **Discount value** (e.g. `10`) and **Valid till** (e.g. a future date). Click **Save**.
7. **Expected:** Success message; table shows the discount (e.g. `10%`) and **Valid till** date.
8. Click **Discount** again on the same row → change value or click **Remove discount**.
9. **Expected:** Modal works; discount updates or is removed.

**If the button does nothing:** Ensure Bootstrap JS loads before the page script (the fix: Bootstrap script is placed before the inline script in `pharmacy_dashboard.html`). Hard-refresh the page (Ctrl+F5).

---

## 3. Test User Search – Discount visible to users

**Goal:** When a user searches for a medicine, results show discount and validity.

1. As **Pharmacy**, set a discount for at least one medicine (Step 2).
2. Open a new incognito window or another browser, go to **http://localhost:5000/user** (or click **Find Medicine** in the navbar).
3. In **Find Medicine**, enter the name of the medicine that has a discount (e.g. partial name). Click **Search**.
4. **Expected:** The table has a **Discount** column showing e.g. `10% off` and `Valid till YYYY-MM-DD` for that pharmacy’s row. Other rows without discount show “—”.

---

## 4. Test Blockchain (tamper-proof audit log)

**Goal:** Verify that discount changes, expiry changes, and inventory updates are recorded in an immutable audit chain.

**What is logged (tamper-proof):**
- **Discount:** set or remove (before/after).
- **Expiry change:** when a pharmacy changes expiry (manual edit or CSV upload).
- **Inventory:** add, update, remove, quantity change, bulk upload.

**How to verify in Firebase:**

1. Go to [Firebase Console](https://console.firebase.google.com) → your project → **Firestore Database**.
2. Check collections:
   - **`audit_chain`**  
     - Documents: `block_0`, `block_1`, …  
     - Each has: `index`, `previous_hash`, `timestamp`, `payload`, `hash`.  
     - `payload` contains `type` (`inventory`, `discount`, `expiry_change`), `pharmacy_email`, `action`, `before`, `after`.
   - **`audit_chain_meta`**  
     - Document `state`: `last_index`, `last_hash`.

**Step-by-step test:**

1. **Generate audit events**
   - Log in as **Pharmacy**.
   - **Set a discount** on a medicine (Discount → set value and valid till → Save).
   - **Change expiry:** Upload a CSV that updates the same medicine with a **different** expiry date (or use “Add one medicine manually” to update an existing one if your app supports it).  
     Alternatively, use “Load invoice sheet” with a CSV that has a different expiry for an existing medicine.
   - Optionally: **Quick Sell** (quantity change) or **Remove expired** (remove).

2. **Check Firestore**
   - Open **Firestore** → **audit_chain**.
   - You should see new documents (e.g. `block_1`, `block_2`, …) with:
     - `payload.type` = `discount` or `expiry_change` or `inventory`
     - `payload.pharmacy_email` = your pharmacy email
     - `payload.before` and `payload.after` (for discount/expiry_change)
   - Open **audit_chain_meta** → **state**: `last_index` should match the latest block number; `last_hash` is that block’s hash.

3. **Tamper-proof property**
   - Each block’s `hash` = SHA-256 of `index + previous_hash + timestamp + payload`.
   - If someone edits an old block in Firestore, its `hash` would no longer match the stored value, and the next block’s `previous_hash` would not match. So the chain is **tamper-evident**.

---

## 5. Pharmacy workflow – Invoice sheet first

**Goal:** Use “Load invoice sheet” as the main way to update stock (distributor sends invoice sheets to pharmacy).

1. Log in as **Pharmacy**.
2. On **Pharmacy Dashboard**, the first main section is **📄 Load invoice sheet**.
   - **Invoice / ERP format (recommended):** Use when the distributor sends a sheet with columns:  
     `medicine_name, batch_no, quantity, expiry_date, distributor_name, purchase_date, pharmacy_email`
   - **Simple format:** Columns: `name, quantity, expiry, pharmacy_email`
3. Prepare a CSV with the required columns (or use `sample_csvs/erp_bulk_medicines.csv` as a template).
4. Click **Choose File** → select the CSV → **Load invoice sheet** (or **Upload CSV** for simple format).
5. **Expected:** Success message; medicines table and stats update. Any **expiry change** for an existing medicine is written to the blockchain audit (see Step 4).
6. **Add one item (optional):** Use the collapsible “➕ Add one medicine manually (optional)” only for a single entry; primary flow is invoice upload.

---

## 6. Quick checklist

| Feature              | How to test                                                                 | Expected result                          |
|----------------------|-----------------------------------------------------------------------------|------------------------------------------|
| Discount button      | Pharmacy → Discount on a row → set value & date → Save                     | Modal opens; discount saved and displayed |
| User sees discount   | User → Find Medicine → search → check table                                | Discount column shows % or Rs off + valid till |
| Blockchain audit     | Do discount set + expiry change (or upload) → Firestore → audit_chain      | New blocks with type discount/expiry_change/inventory |
| Invoice sheet        | Pharmacy → Load invoice sheet → upload CSV                                 | Stock updated; expiry changes audited    |

---

## 7. Troubleshooting

- **Discount button not opening modal:** Hard refresh (Ctrl+F5). Ensure Bootstrap JS is loaded (check browser console for errors).
- **User search shows no discount:** Ensure the medicine has discount set and `discount_valid_till` is in the document; search for a medicine that exists and has a discount.
- **No blocks in audit_chain:** Ensure Firestore is connected (no “CSV fallback” at startup). Perform at least one action that triggers audit (e.g. set discount, upload CSV that changes expiry).
- **Email alerts:** See **EMAIL_SETUP.md** and use Admin → “Send expiry alerts now” to test.
