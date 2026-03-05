#!/usr/bin/env python3
"""
Script to create initial users from existing pharmacy data
Creates admin and pharmacy users with default passwords
"""
import os
import pandas as pd
from datetime import datetime

# Initialize Firestore
db = None
try:
    if os.path.exists("serviceAccountKey.json"):
        import firebase_admin
        from firebase_admin import credentials, firestore
        cred = credentials.Certificate("serviceAccountKey.json")
        try:
            firebase_admin.initialize_app(cred)
        except ValueError:
            # Already initialized
            pass
        db = firestore.client()
        print("✅ Firestore initialized.")
    else:
        print("❌ serviceAccountKey.json not found. Please add it first.")
        exit(1)
except Exception as e:
    print(f"❌ Firestore init error: {e}")
    exit(1)

def create_admin_user():
    """Create default admin user"""
    admin_email = "admin@medscope.com"
    admin_password = "admin123"  # Change this in production!
    admin_name = "MedScope Admin"
    
    # Check if admin already exists
    user_doc = db.collection("users").document(admin_email).get()
    if user_doc.exists:
        print(f"⚠️  Admin user already exists: {admin_email}")
        return admin_email, admin_password
    
    # Create admin user
    user_data = {
        "email": admin_email,
        "password": admin_password,
        "role": "admin",
        "name": admin_name,
        "phone": "",
        "created_at": datetime.now().isoformat()
    }
    
    db.collection("users").document(admin_email).set(user_data)
    print(f"✅ Admin user created: {admin_email}")
    return admin_email, admin_password

def create_pharmacy_users():
    """Create pharmacy users from CSV file"""
    csv_path = "sample_csvs/hyd_pharmacies.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return []
    
    df = pd.read_csv(csv_path)
    default_password = "pharmacy123"  # Default password for all pharmacies
    
    created_users = []
    
    for _, row in df.iterrows():
        email = str(row["pharmacy_email"]).strip()
        pharmacy_name = str(row["pharmacy_name"]).strip()
        address = str(row.get("address", "")).strip()
        lat = float(row.get("lat", 17.3850))
        lon = float(row.get("lon", 78.4867))
        
        # Check if user already exists
        user_doc = db.collection("users").document(email).get()
        if user_doc.exists:
            print(f"⚠️  User already exists: {email}")
            created_users.append({
                "email": email,
                "password": "*** (already exists - use existing password)",
                "role": "pharmacy",
                "name": pharmacy_name
            })
            continue
        
        # Create user
        user_data = {
            "email": email,
            "password": default_password,
            "role": "pharmacy",
            "name": pharmacy_name,
            "phone": "",
            "created_at": datetime.now().isoformat()
        }
        
        # Create pharmacy entry
        pid = email.replace("@", "_at_").replace(".", "_dot_")
        pharm_data = {
            "pharmacy_email": email,
            "pharmacy_name": pharmacy_name,
            "address": address,
            "lat": lat,
            "lon": lon,
            "phone": ""
        }
        
        db.collection("users").document(email).set(user_data)
        db.collection("pharmacies").document(pid).set(pharm_data, merge=True)
        
        print(f"✅ Pharmacy user created: {email} ({pharmacy_name})")
        created_users.append({
            "email": email,
            "password": default_password,
            "role": "pharmacy",
            "name": pharmacy_name
        })
    
    return created_users

def main():
    print("=" * 60)
    print("MEDSCOPE USER CREATION SCRIPT")
    print("=" * 60)
    print()
    
    # Create admin
    print("Creating Admin User...")
    admin_email, admin_password = create_admin_user()
    print()
    
    # Create pharmacy users
    print("Creating Pharmacy Users from CSV...")
    pharmacy_users = create_pharmacy_users()
    print()
    
    # Print credentials
    print("=" * 60)
    print("LOGIN CREDENTIALS")
    print("=" * 60)
    print()
    
    print("🔑 ADMIN LOGIN:")
    print(f"   Email: {admin_email}")
    print(f"   Password: {admin_password}")
    print(f"   Role: admin")
    print(f"   URL: http://localhost:5000/login?role=admin")
    print()
    
    print("🔑 PHARMACY LOGINS:")
    print(f"   Default Password for ALL pharmacies: pharmacy123")
    print()
    
    if pharmacy_users:
        print("   Available Pharmacy Accounts:")
        for i, user in enumerate(pharmacy_users[:10], 1):  # Show first 10
            print(f"   {i}. Email: {user['email']}")
            print(f"      Name: {user['name']}")
            print(f"      Password: {user['password']}")
            print()
        
        if len(pharmacy_users) > 10:
            print(f"   ... and {len(pharmacy_users) - 10} more pharmacies")
            print()
        
        print("   Example Pharmacy Login:")
        print(f"   Email: {pharmacy_users[0]['email']}")
        print(f"   Password: {pharmacy_users[0]['password']}")
        print(f"   URL: http://localhost:5000/login?role=pharmacy")
    else:
        print("   No pharmacy users created.")
    
    print()
    print("=" * 60)
    print("⚠️  IMPORTANT SECURITY NOTES:")
    print("=" * 60)
    print("1. These are DEFAULT passwords - CHANGE them after first login!")
    print("2. In production, use strong passwords and hash them properly")
    print("3. Store this file securely or delete it after use")
    print("=" * 60)
    
    # Save credentials to file
    credentials_file = "LOGIN_CREDENTIALS.txt"
    with open(credentials_file, "w") as f:
        f.write("=" * 60 + "\n")
        f.write("MEDSCOPE LOGIN CREDENTIALS\n")
        f.write("=" * 60 + "\n\n")
        f.write("ADMIN LOGIN:\n")
        f.write(f"Email: {admin_email}\n")
        f.write(f"Password: {admin_password}\n")
        f.write(f"Role: admin\n\n")
        f.write("PHARMACY LOGINS:\n")
        f.write(f"Default Password: pharmacy123\n\n")
        for user in pharmacy_users:
            f.write(f"Email: {user['email']}\n")
            f.write(f"Name: {user['name']}\n")
            f.write(f"Password: {user['password']}\n\n")
    
    print(f"\n✅ Credentials saved to: {credentials_file}")
    print("   (Keep this file secure!)")

if __name__ == "__main__":
    main()

