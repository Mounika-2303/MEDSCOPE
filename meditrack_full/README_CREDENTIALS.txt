================================================================================
MEDSCOPE - QUICK LOGIN CREDENTIALS
================================================================================

STEP 1: Create Users
---------------------
Run this command:
    python create_users.py

This will create:
- 1 Admin user
- All pharmacy users from your CSV file

================================================================================
DEFAULT CREDENTIALS
================================================================================

ADMIN LOGIN:
------------
Email:    admin@medscope.com
Password: admin123
Role:     admin
URL:      http://localhost:5000/login?role=admin

PHARMACY LOGINS:
----------------
Default Password: pharmacy123

Use ANY email from your hyd_pharmacies.csv file, for example:
- apollohyd@gmail.com
- medplushyd@gmail.com
- netmedshyd@gmail.com
- localshop1@gmail.com
- localshop2@gmail.com
... and all others in your CSV

Login URL: http://localhost:5000/login?role=pharmacy

================================================================================
EXAMPLE LOGINS
================================================================================

Example 1 - Admin:
------------------
URL:      http://localhost:5000/login?role=admin
Email:    admin@medscope.com
Password: admin123

Example 2 - Pharmacy (Apollo):
-------------------------------
URL:      http://localhost:5000/login?role=pharmacy
Email:    apollohyd@gmail.com
Password: pharmacy123

Example 3 - Pharmacy (Local Shop):
-----------------------------------
URL:      http://localhost:5000/login?role=pharmacy
Email:    localshop1@gmail.com
Password: pharmacy123

================================================================================
GUEST MODE (NO LOGIN NEEDED)
================================================================================
Users can search medicines without login:
- Map Search: http://localhost:5000/map
- Quick Search: http://localhost:5000/user

================================================================================
IMPORTANT NOTES
================================================================================
1. These are DEFAULT passwords - change them after first login!
2. All credentials are saved to: LOGIN_CREDENTIALS.txt
3. Keep credentials file secure
4. In production, use strong passwords

================================================================================

