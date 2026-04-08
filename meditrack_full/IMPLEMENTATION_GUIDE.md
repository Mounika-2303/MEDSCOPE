# MedScope - Complete Implementation Guide

## ✅ Features Implemented

### 1. Role-Based Access Control (RBAC)
- **User Login**: Regular users can search for medicines
- **Pharmacy Login**: Each pharmacy can login and manage their own inventory
- **Admin Login**: Admin can monitor the entire system

### 2. Authentication System
- Login/Register pages for all user types
- Session-based authentication
- Role-based route protection

### 3. Expiry Alert System (FIXED)
- ✅ Alerts sent to registered email addresses
- ✅ SMS notifications (placeholder - can integrate free SMS service)
- ✅ Alerts shown in Admin Dashboard
- ✅ Alerts for both expired and expiring soon medicines
- ✅ Daily scheduled job at 9 AM

### 4. Pharmacy Dashboard (FIXED)
- ✅ Pie chart with correct colors:
  - **Expired = Red** (#dc3545)
  - **Expiring Soon = Orange** (#ff9800)
  - **Available = Green** (#28a745)
- ✅ Shows only logged-in pharmacy's medicines
- ✅ Statistics cards for quick overview

### 5. Real-Time Dataset
- ✅ Added 10 local small shops/pharmacies
- ✅ Added medicines like "Dolo 650mg" in nearby shops
- ✅ Added other common medicines (Crocin, Calpol, Disprin, Combiflam, Vicks Action)
- ✅ Medicines distributed across multiple small shops for realistic search results

### 6. Cloud Services (All Free Tier)
- ✅ **Firebase Firestore**: Database (Free tier: 50K reads/day, 20K writes/day)
- ✅ **Firebase Authentication**: User management (Free tier: Unlimited)
- ✅ **Gmail SMTP**: Email alerts (Free - uses Gmail app password)
- ✅ **SMS**: Placeholder for free SMS service (can use Twilio trial or similar)

## 📋 Step-by-Step Setup Instructions

### Step 1: Install Dependencies
```bash
cd meditrack_full
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Create a `.env` file in the `meditrack_full` directory:
```env
GMAIL_SENDER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-gmail-app-password
ADMIN_EMAIL=admin@example.com
SECRET_KEY=your-secret-key-here-change-in-production
```

**To get Gmail App Password:**
1. Go to Google Account settings
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate a new app password for "Mail"
5. Use that password in `.env`

### Step 3: Firebase Setup (Free Tier)
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project (or use existing)
3. Enable Firestore Database
4. Go to Project Settings > Service Accounts
5. Generate new private key
6. Download the JSON file
7. Save it as `serviceAccountKey.json` in `meditrack_full/` directory

**Firebase Free Tier Limits:**
- Firestore: 50,000 reads/day, 20,000 writes/day
- Authentication: Unlimited users
- Storage: 5 GB

### Step 4: Run the Application
```bash
python app.py
```

The application will run on `http://localhost:5000`

### Step 5: Create Initial Users

#### Create Admin User:
1. Go to `/register?role=admin`
2. Register with:
   - Email: admin@medscope.com
   - Password: (your choice)
   - Role: Admin

#### Create Pharmacy User:
1. Go to `/register?role=pharmacy`
2. Register with:
   - Email: pharmacy@example.com
   - Password: (your choice)
   - Role: Pharmacy
   - Address, Lat, Lon: (pharmacy location)

#### Create Regular User:
1. Go to `/register?role=user`
2. Register with email and password

## 🔧 Making Changes to the Code

### Adding a New Route:
1. Open `app.py`
2. Add route decorator:
```python
@app.route("/your_route")
@login_required(role="pharmacy")  # Optional: specify role
def your_function():
    return render_template("your_template.html")
```

### Adding a New Medicine:
1. Login as Pharmacy
2. Go to Pharmacy Dashboard
3. Use "Add Single Medicine" form
4. Or upload CSV with format: `name, quantity, expiry, pharmacy_email`

### Modifying Alert Schedule:
In `app.py`, find the scheduler section:
```python
scheduler.add_job(send_expiry_alerts, "cron", hour=9, minute=0)
```
Change `hour` and `minute` as needed.

### Changing Pie Chart Colors:
In `pharmacy_dashboard.html`, find the Chart.js configuration:
```javascript
backgroundColor: [
  '#28a745',  // Green for Available
  '#ff9800',  // Orange for Expiring Soon
  '#dc3545'   // Red for Expired
]
```

### Adding More Sample Data:
1. Edit `sample_csvs/hyd_pharmacies.csv` to add pharmacies
2. Edit `sample_csvs/erp_bulk_medicines.csv` to add medicines
3. Format must match existing columns

## 📊 Database Structure

### Firestore Collections:

1. **users** (Document ID = email)
   - email
   - password (hash in production)
   - role (user/pharmacy/admin)
   - name
   - phone
   - created_at

2. **pharmacies** (Document ID = email with @ and . replaced)
   - pharmacy_email
   - pharmacy_name
   - address
   - lat
   - lon
   - phone

3. **medicines** (Document ID = name_pharmacy_email)
   - name
   - quantity
   - expiry
   - status (Available/Expiring Soon/Expired)
   - pharmacy_email
   - batch_no (optional)
   - distributor_name (optional)
   - purchase_date (optional)

4. **alerts**
   - medicine_name
   - pharmacy_email
   - expiry_date
   - days_left
   - sent_on
   - status (Sent/Failed)
   - alert_type (Expired/Expiring Soon)

5. **bills**
   - customer_name
   - medicine_name
   - quantity_sold
   - price_per_unit
   - total_price
   - sold_at
   - pharmacy_email

6. **violations**
   - pharmacy_email
   - medicine_name
   - attempted_on
   - reason

## 🚀 Deployment Notes

### For Production:
1. Change `SECRET_KEY` in `.env` to a strong random string
2. Hash passwords (use bcrypt or similar)
3. Use environment variables for all sensitive data
4. Enable HTTPS
5. Set up proper error logging
6. Configure Firebase security rules
7. Set up proper backup strategy

### Firebase Security Rules (Example):
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
    match /medicines/{medicineId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
        (resource.data.pharmacy_email == request.auth.token.email || 
         request.auth.token.role == 'admin');
    }
  }
}
```

## 📝 Testing Checklist

- [ ] Register as User, Pharmacy, Admin
- [ ] Login with each role
- [ ] Pharmacy can add medicines
- [ ] Pharmacy dashboard shows only their medicines
- [ ] Pie chart shows correct colors
- [ ] Search for "dolo" shows nearby small shops
- [ ] Map search works correctly
- [ ] Expiry alerts are sent (check email)
- [ ] Admin dashboard shows alerts
- [ ] Billing system works
- [ ] PDF generation works

## 🐛 Troubleshooting

### Email not sending:
- Check Gmail app password is correct
- Verify 2-Step Verification is enabled
- Check spam folder

### Firebase errors:
- Verify `serviceAccountKey.json` is in correct location
- Check Firebase project is active
- Verify Firestore is enabled

### Login not working:
- Check session is enabled
- Verify SECRET_KEY is set
- Clear browser cookies

### Medicines not showing:
- Check pharmacy_email matches logged-in user
- Verify Firestore has data
- Check CSV format if using fallback

## 📞 Support

For issues or questions:
1. Check Firebase console for errors
2. Check application logs
3. Verify all environment variables are set
4. Ensure all dependencies are installed

## 🎯 Next Steps (Optional Enhancements)

1. **SMS Integration**: Use Twilio trial (free credits) or similar
2. **Push Notifications**: Firebase Cloud Messaging (free tier)
3. **Analytics**: Firebase Analytics (free)
4. **Image Upload**: Firebase Storage (5GB free)
5. **Real-time Updates**: Firestore real-time listeners
6. **Mobile App**: React Native with Firebase

---

**All cloud services used are within free tier limits!**

