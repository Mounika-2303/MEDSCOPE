# MedScope - Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create `.env` File
Create `meditrack_full/.env`:
```env
GMAIL_SENDER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-gmail-app-password
ADMIN_EMAIL=admin@example.com
SECRET_KEY=change-this-to-random-string
```

### 3. Add Firebase Credentials
- Download `serviceAccountKey.json` from Firebase Console
- Place it in `meditrack_full/` directory

### 4. Run Application
```bash
python app.py
```

### 5. Access Application
Open browser: `http://localhost:5000`

## 👥 Login Credentials

### Quick Setup (Recommended):
Run this script to create all users from your existing CSV data:
```bash
python create_users.py
```

This creates:
- **Admin**: `admin@medscope.com` / `admin123`
- **All Pharmacies**: Use any email from `hyd_pharmacies.csv` / Password: `pharmacy123`

### Manual Registration (Alternative):
1. **Admin**: Go to `http://localhost:5000/register?role=admin`
2. **Pharmacy**: Go to `http://localhost:5000/register?role=pharmacy`
3. **User**: Go to `http://localhost:5000/register?role=user`

### Using Existing Pharmacy Emails:
Your CSV has pharmacies like:
- `apollohyd@gmail.com`
- `medplushyd@gmail.com`
- `localshop1@gmail.com`
- ... etc.

After running `create_users.py`, login with:
- **Email**: Any pharmacy email from CSV
- **Password**: `pharmacy123`
- **Role**: pharmacy

## 🔍 Test Features

### Test Medicine Search:
1. Login as User
2. Go to Map page
3. Search for "dolo"
4. See nearby small shops with Dolo available

### Test Pharmacy Dashboard:
1. Login as Pharmacy
2. Add a medicine with expiry date in past (to test expired)
3. Add a medicine expiring in 20 days (to test expiring soon)
4. Check pie chart colors:
   - Red = Expired
   - Orange = Expiring Soon
   - Green = Available

### Test Alerts:
1. Add medicine with expiry date in past or within 7 days
2. Wait for scheduled job (or manually trigger)
3. Check Admin Dashboard > Alert Log
4. Check registered email for alert

## 📋 Key Features

✅ Role-based login (User/Pharmacy/Admin)
✅ Each pharmacy manages own inventory
✅ Expiry alerts via email/SMS
✅ Pie chart with correct colors
✅ Real-time medicine search with nearby shops
✅ Map-based pharmacy finder
✅ Billing system with PDF generation

## 🆘 Need Help?

See `IMPLEMENTATION_GUIDE.md` for detailed documentation.

