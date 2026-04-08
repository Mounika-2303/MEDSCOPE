# MedScope – Complete Setup Guide (Windows 11, Python 3.8)

This guide will help you run MedScope on **Windows 11** with **Python 3.8**. All implemented features work on this setup.

---

## Step 1: Check Python Version

Open **Command Prompt** or **PowerShell** and run:

```
python --version
```

You should see `Python 3.8.x`. If not, install Python 3.8 from [python.org](https://www.python.org/downloads/).

---

## Step 2: Create Virtual Environment (Recommended)

```cmd
cd c:\Users\kandi\OneDrive\Desktop\meditrack_full
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in the prompt.

---

## Step 3: Install Dependencies

With the virtual environment active:

```
pip install -r requirements.txt
```

If you see any errors, install packages one by one:

```
pip install Flask==2.2.5
pip install firebase-admin==6.1.0
pip install pandas==2.0.3
pip install python-dotenv==1.0.1
pip install APScheduler==3.10.4
pip install reportlab==3.6.12
pip install fpdf==1.7.2
pip install pyjwt==2.8.0
```

---

## Step 4: Firebase / Firestore Setup

### 4.1 Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project (or use existing)
3. Go to **Project Settings** (gear icon) → **Service accounts**
4. Click **Generate new private key**

### 4.2 Add Service Account Key

1. Save the downloaded JSON file
2. Rename it to `serviceAccountKey.json`
3. Place it in the project root:
   ```
   meditrack_full\
   ├── app.py
   ├── serviceAccountKey.json   ← HERE
   ├── requirements.txt
   └── ...
   ```

**Important:** Do not commit this file to Git. Add `serviceAccountKey.json` to `.gitignore`.

### 4.3 Enable Firestore

1. In Firebase Console, go to **Build** → **Firestore Database**
2. Click **Create database**
3. Choose **Start in test mode** (for development)
4. Select a region and create

---

## Step 5: Environment Variables (.env)

Create or edit the `.env` file in the project root:

```
# Required for email alerts (expiry alerts, etc.)
GMAIL_SENDER=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
ADMIN_EMAIL=admin@yourdomain.com

# Optional: Secret for session (change in production)
SECRET_KEY=your-secret-key-here
```

### 5.1 Gmail App Password

1. Use a Gmail account
2. Enable 2-Step Verification: [Google Account Security](https://myaccount.google.com/security)
3. Go to **App passwords** → Generate new app password
4. Copy the 16-character password (with or without spaces) and paste in `GMAIL_APP_PASSWORD`

---

## Step 6: Firestore Index (Optional – for Violations Sorting)

If you see an error about a missing index when loading the Admin dashboard:

1. Open the error link in the browser (Firebase will offer to create the index)
2. Or go to [Firestore Indexes](https://console.firebase.google.com/) → **Indexes**
3. Add a composite index:
   - Collection: `violations`
   - Field: `attempted_on` (Descending)

The app works even without this index – it falls back to in-memory sorting.

---

## Step 7: Folders and Sample Data

Ensure these exist:

```
meditrack_full\
├── static\
│   ├── bills\          (auto-created)
│   └── uploads\
│       └── license\    (auto-created on first pharmacy registration)
├── sample_csvs\
│   ├── hyd_pharmacies.csv
│   ├── erp_bulk_medicines.csv
│   └── medicine_data.csv
```

If `sample_csvs` is missing, the app can still run with Firestore.

---

## Step 8: Run the Application

```cmd
cd c:\Users\kandi\OneDrive\Desktop\meditrack_full
venv\Scripts\activate
python app.py
```

You should see:

```
✅ Firestore initialized.
✅ Blockchain audit logging enabled.
 * Running on http://127.0.0.1:5000
```

Open a browser and go to: **http://127.0.0.1:5000**

---

## Step 9: First-Time Usage

| Action | How |
|--------|-----|
| Create Admin | Manually add a user in Firestore `users` with `role: "admin"` |
| Create Pharmacy | Register at `/register` with role Pharmacy → Admin approves |
| Create User | Register at `/register` with role User |
| Guest Search | Use Map (`/map`) or Quick Search (`/user`) without login |

---

## Features Checklist (All Work on Python 3.8 + Windows 11)

| Feature | Notes |
|---------|-------|
| Map + Starting Point | Uses OpenStreetMap Nominatim – **no API key** |
| Email Updates Opt-in | Uses Firestore `user_medicine_interests` |
| User Search + View Location | Case-insensitive, modal map on same page |
| Admin Violations/Alerts | Sorted by most recent first |
| Auto Discount Removal | Runs daily at 00:05 |
| Pharmacy License Verification | Upload document at registration, view in Admin |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside venv |
| Firestore not connecting | Check `serviceAccountKey.json` path and content |
| Email not sending | Verify Gmail App Password, 2FA enabled |
| Port 5000 in use | Change in `app.py`: `app.run(debug=True, port=5001)` |
| `Query.DESCENDING` error | App falls back to in-memory sort; no action needed |

---

## Optional: Run Without Firebase

If you skip `serviceAccountKey.json`, the app runs in **CSV fallback mode** using `sample_csvs/`. Most features work, but Firestore-dependent features (pharmacy approval, user interests, etc.) are limited.
