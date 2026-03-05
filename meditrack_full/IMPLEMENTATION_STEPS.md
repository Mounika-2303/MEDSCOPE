# MedScope – Step-by-Step Implementation (Security & UX Fixes)

This document describes the changes made to address pharmacy authenticity, audit tampering visibility, admin-only login, and home page layout, plus how to use and extend them.

---

## 1. Pharmacy Registration – Authentic / Approval-Based Flow

### Problem
Anyone could register as a pharmacy and upload medicines without verification.

### What Was Done

- **Pending status**  
  New pharmacy registrations are stored with `pharmacy_status: "pending"`. They cannot log in until an admin approves.

- **Optional license number**  
  Pharmacy registration form has an optional “License / Registration Number” field, stored in the `pharmacies` collection for admin verification.

- **Login check**  
  When a user logs in as “Pharmacy”, the app checks the `pharmacies` document for that email:
  - If `pharmacy_status` is missing (old data), it is treated as **approved** so existing pharmacies keep working.
  - If `pharmacy_status` is **"pending"** or **"rejected"**, login is denied with:  
    *“Your pharmacy registration is pending approval. Contact admin.”*

- **Admin approval**  
  In the Admin Dashboard:
  - **Pending pharmacy approvals** section lists all pharmacies with `pharmacy_status == "pending"`.
  - Each row has **Approve** and **Reject**.
  - Approve sets `pharmacy_status: "approved"` (pharmacy can then log in).
  - Reject sets `pharmacy_status: "rejected"`.

### Step-by-Step Usage

1. **Pharmacy**  
   - Go to Home → Pharmacy → Register.  
   - In “Register As”, select **Pharmacy** so that the extra block appears (License #, Address, Lat/Lon).  
   - Fill name, email, password, phone, and the **Pharmacy details** section (license number recommended, address, coordinates).  
   - Submit → account created with status **pending**.  
   - Try Login → blocked until approved.

2. **Admin**  
   - Login as admin.  
   - Open Admin Dashboard.  
   - The **“Pharmacy approvals”** section is always visible. If there are pending pharmacies, they appear in the table with Approve/Reject.  
   - **How to verify:** Use the pharmacy name, address, **License #**, and phone. Cross-check the license with your state/regulatory records, or contact the pharmacy by phone/email. Approve only after you are satisfied they are legitimate.  
   - Click **Approve** for a pharmacy → that pharmacy can then log in.

3. **Optional**  
   - Manually in Firestore: set `pharmacies/<pid>.pharmacy_status` to `"approved"` for existing pharmacies if needed.

### Files Touched

- `app.py`: register (pharmacy_status, license_number, block admin registration); login (pharmacy status check); `approve_pharmacy`, `reject_pharmacy` routes; admin view now passes `pending_pharmacies`.
- `templates/register.html`: pharmacy notice, license number field, “Register as” dropdown no longer includes Admin.

---

## 2. Blockchain / Invoice Tampering – Auditing & Violations

### Problem
- Invoice data (CSV → medicines) can be changed in Firestore.  
- Violations were only stored in the backend; no one saw them.  
- Need a way to detect audit-chain tampering and surface it.

### What Was Done

- **Audit chain verification**  
  In `blockchain_audit.py`, added `verify_chain()` that:
  - Walks all blocks in `audit_chain` from 0 to `last_index`.
  - Recomputes each block’s hash from (index + previous_hash + timestamp + payload).
  - If any stored hash does not match the recomputed hash, the chain is considered **tampered** (e.g. someone changed invoice/expiry data in a block).
  - Returns `(is_valid: bool, broken_index: Optional[int])`.

- **Tampering → violation**  
  Admin route `POST /admin/verify_audit`:
  - Calls `verify_chain()`.
  - If the chain is invalid, adds a document to the `violations` collection with reason like:  
    *“Audit chain tampering detected at block_X. Invoice/expiry data may have been altered.”*

- **Violations visible in Admin**  
  - Admin Dashboard now has a **Violations** section that reads from the `violations` collection (last 100, sorted by `attempted_on`).
  - Shows: time, pharmacy/entity, medicine/details, reason.  
  - This includes both:
    - Existing violations (e.g. attempted sale of expired medicine, quick-sell expired).
    - New violations from audit tampering when admin runs “Verify audit chain”.

- **“Verify audit chain” button**  
  - On Admin Dashboard, **Verify audit chain** calls `/admin/verify_audit` (POST).
  - Displays “Chain valid” or “Tampering at block X. Violation logged.” and refreshes the page so the new violation appears in the table.

### Can Invoice Sheets Be Changed?

- **In Firestore:** Yes. The `medicines` collection (and any CSV that was loaded into it) can be edited directly in the database.
- **Audit trail:** All inventory/expiry changes that go through the app are appended to the blockchain-style audit chain. If someone later changes a **past block** in `audit_chain` (e.g. to hide an expiry change), the chain’s hashes no longer match.
- **Detection:** When admin runs “Verify audit chain”, tampering is detected and a violation is logged and shown in the Violations table. So even if not everyone checks the backend, the admin can run verification and see violations in the UI.

### Step-by-Step Usage

1. **Regular monitoring**  
   - Admin logs in → Admin Dashboard.  
   - Click **Verify audit chain** periodically.  
   - If tampering is found, a violation is created and the Violations table shows it.

2. **View violations**  
   - Scroll to “Violations (expired sale attempts & audit tampering)” on the same dashboard.  
   - All violations (expired sales + audit tampering) are listed there.

3. **Optional improvements (future)**  
   - Run `verify_chain()` on a schedule (e.g. cron) and log violations automatically.  
   - Add a public or pharmacist-facing “Chain verified at …” badge based on last successful verification.

### Files Touched

- `blockchain_audit.py`: added `verify_chain()`.
- `app.py`: admin view passes `violations`; added `verify_audit` route that calls `verify_chain()` and writes to `violations` when invalid.
- `templates/admin_dashboard.html`: Violations table, Pending pharmacies section, “Verify audit chain” button and script.

---

## 3. Admin Login Page – No Register Link

### Problem
On the login page, when role was “Admin”, a “Register here” link still appeared, which is inappropriate for admin accounts.

### What Was Done

- In `templates/login.html`, the line “Don’t have an account? Register here” is shown only when `role != 'admin'`.
- So when an admin opens the login page (e.g. from Home → Admin → Login), only the login form and “Back to Home” are shown; no register link.

### Step-by-Step

- Go to Home → Admin → Login.  
- Confirm only credentials and “Back to Home” are shown; no “Register here”.

### Files Touched

- `templates/login.html`: wrapped the register link in `{% if role != 'admin' %}`.

---

## 4. Home Page – Equal Login Box Sizes (User / Pharmacy / Admin)

### Problem
The User login/register box appeared larger than the Admin and Pharmacy boxes because User had two buttons and more content.

### What Was Done

- Added a CSS class `login-role-card` for the three role cards:
  - `min-height: 180px` so all three cards have the same height.
  - Card body uses flex so content and buttons are spaced consistently.
- Wrapped the buttons in each card in a `<div>` so layout is uniform.

### Step-by-Step

- Open Home (not logged in).  
- Check that the three cards (User, Pharmacy, Admin) have the same height and aligned layout.

### Files Touched

- `templates/index.html`: style for `.login-role-card`, added class to all three cards and a wrapper div for buttons.

---

## 5. Block Admin Registration

### Problem
Admin accounts should not be creatable via the public register page.

### What Was Done

- **Register route**  
  - If someone opens `/register?role=admin` (GET) or submits with role=admin (POST), they are redirected to the login page (with an optional message that admin accounts cannot be registered).
- **Register template**  
  - The “Register as” dropdown no longer includes “Admin”; only User and Pharmacy.

### Step-by-Step

- Try opening `/register?role=admin` → should redirect to login.  
- On the register page, “Register as” should only list User and Pharmacy.

### Files Touched

- `app.py`: at start of `register()`, redirect when role is admin; reject POST with role=admin.
- `templates/register.html`: removed Admin from the role dropdown.

---

## Summary Table

| Flaw / Request | Solution |
|----------------|----------|
| Pharmacy registration not authentic | Pending status + admin approval; optional license #; login blocked until approved. |
| Invoice/data tampering; violations only in backend | `verify_chain()` in blockchain_audit; admin “Verify audit chain” logs tampering to violations; Violations table on Admin Dashboard. |
| Admin login page showed Register | Register link hidden when role is admin. |
| User login box larger than Admin/Pharmacy | Same-height cards via `.login-role-card` and flex layout. |
| Admin should not register from app | Admin removed from register dropdown; register route redirects/rejects role=admin. |

---

## Quick Test Checklist

1. **Pharmacy approval**  
   - Register new pharmacy → try login (should fail).  
   - Admin approves → pharmacy login (should succeed).

2. **Violations**  
   - As pharmacy, try to sell expired medicine (billing or quick sell) → violation appears in Admin → Violations.  
   - Admin clicks “Verify audit chain” → if chain is valid, “Chain valid”; if you manually corrupt a block in Firestore and verify again, a tampering violation appears.

3. **Admin login**  
   - Open login with role=admin → no “Register here” link.

4. **Home layout**  
   - Home page: User, Pharmacy, Admin cards same height.

5. **Admin registration blocked**  
   - Visit `/register?role=admin` → redirect to login; register form has no Admin option.

---

## Export CSV (Admin Dashboard)

**What it does:** The **Export CSV** button downloads a CSV file containing **all medicines** in the system: name, quantity, expiry date, pharmacy email, and status (Available / Expiring Soon / Expired). It is useful for:

- Backing up inventory data
- Analysing stock or expiry in Excel/Sheets
- Auditing what each pharmacy has listed

Only admins can access this route; the file is generated on demand when you click the button.

---

## Optional Next Steps

- **Password hashing:** Replace plaintext password storage with bcrypt or similar.  
- **Scheduled chain verification:** Run `verify_chain()` on a cron job and log violations.  
- **Email to admin on violation:** When a violation is added (expired sale or tampering), send an email to `ADMIN_EMAIL`.  
- **Pharmacy license verification:** Manual or automated check of `license_number` before approval.
