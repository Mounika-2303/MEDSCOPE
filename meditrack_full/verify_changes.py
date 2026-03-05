#!/usr/bin/env python3
"""
Verification script to check if all new features are implemented
"""
import os
import re

print("=" * 60)
print("MEDSCOPE CHANGES VERIFICATION")
print("=" * 60)

checks = []

# Check 1: Login route exists
print("\n1. Checking for /login route...")
if os.path.exists("app.py"):
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
        if '@app.route("/login"' in content:
            print("   ✅ /login route FOUND")
            checks.append(True)
        else:
            print("   ❌ /login route NOT FOUND")
            checks.append(False)
else:
    print("   ❌ app.py not found")
    checks.append(False)

# Check 2: Register route exists
print("\n2. Checking for /register route...")
if os.path.exists("app.py"):
    if '@app.route("/register"' in content:
        print("   ✅ /register route FOUND")
        checks.append(True)
    else:
        print("   ❌ /register route NOT FOUND")
        checks.append(False)

# Check 3: Login page exists
print("\n3. Checking for login.html template...")
if os.path.exists("templates/login.html"):
    print("   ✅ login.html FOUND")
    checks.append(True)
else:
    print("   ❌ login.html NOT FOUND")
    checks.append(False)

# Check 4: Register page exists
print("\n4. Checking for register.html template...")
if os.path.exists("templates/register.html"):
    print("   ✅ register.html FOUND")
    checks.append(True)
else:
    print("   ❌ register.html NOT FOUND")
    checks.append(False)

# Check 5: Session management
print("\n5. Checking for session management...")
if 'session.get("user_email")' in content:
    print("   ✅ Session management FOUND")
    checks.append(True)
else:
    print("   ❌ Session management NOT FOUND")
    checks.append(False)

# Check 6: Pharmacy dashboard pie chart
print("\n6. Checking for pie chart in pharmacy dashboard...")
if os.path.exists("templates/pharmacy_dashboard.html"):
    with open("templates/pharmacy_dashboard.html", "r", encoding="utf-8") as f:
        pharm_content = f.read()
        if "statusChart" in pharm_content and "Chart.js" in pharm_content:
            print("   ✅ Pie chart FOUND")
            checks.append(True)
        else:
            print("   ❌ Pie chart NOT FOUND")
            checks.append(False)
else:
    print("   ❌ pharmacy_dashboard.html not found")
    checks.append(False)

# Check 7: Pie chart colors (Red for Expired, Orange for Expiring Soon)
print("\n7. Checking pie chart colors...")
if os.path.exists("templates/pharmacy_dashboard.html"):
    if '#dc3545' in pharm_content and '#ff9800' in pharm_content:
        print("   ✅ Correct colors FOUND (Red=#dc3545, Orange=#ff9800)")
        checks.append(True)
    else:
        print("   ❌ Correct colors NOT FOUND")
        checks.append(False)

# Check 8: Expiry alerts for expired medicines
print("\n8. Checking expiry alerts for expired medicines...")
if 'days_left < 0' in content and 'Alert for expired medicines' in content:
    print("   ✅ Expired medicine alerts FOUND")
    checks.append(True)
else:
    print("   ❌ Expired medicine alerts NOT FOUND")
    checks.append(False)

# Check 9: Dolo medicines
print("\n9. Checking for Dolo medicines...")
if os.path.exists("sample_csvs/erp_bulk_medicines.csv"):
    with open("sample_csvs/erp_bulk_medicines.csv", "r", encoding="utf-8") as f:
        med_content = f.read()
        dolo_count = med_content.count("Dolo")
        if dolo_count > 0:
            print(f"   ✅ Dolo medicines FOUND ({dolo_count} entries)")
            checks.append(True)
        else:
            print("   ❌ Dolo medicines NOT FOUND")
            checks.append(False)
else:
    print("   ❌ erp_bulk_medicines.csv not found")
    checks.append(False)

# Check 10: Local shops
print("\n10. Checking for local shops...")
if os.path.exists("sample_csvs/hyd_pharmacies.csv"):
    with open("sample_csvs/hyd_pharmacies.csv", "r", encoding="utf-8") as f:
        pharm_csv = f.read()
        localshop_count = pharm_csv.count("localshop")
        if localshop_count > 0:
            print(f"   ✅ Local shops FOUND ({localshop_count} entries)")
            checks.append(True)
        else:
            print("   ❌ Local shops NOT FOUND")
            checks.append(False)
else:
    print("   ❌ hyd_pharmacies.csv not found")
    checks.append(False)

# Check 11: Pharmacy dashboard filters by logged-in pharmacy
print("\n11. Checking pharmacy dashboard filters by logged-in pharmacy...")
if 'pharmacy_email = session.get("user_email")' in content:
    print("   ✅ Pharmacy filtering FOUND")
    checks.append(True)
else:
    print("   ❌ Pharmacy filtering NOT FOUND")
    checks.append(False)

# Check 12: Navbar has login/logout
print("\n12. Checking navbar for login/logout...")
if os.path.exists("templates/navbar.html"):
    with open("templates/navbar.html", "r", encoding="utf-8") as f:
        navbar_content = f.read()
        if 'session.get("user_email")' in navbar_content and '/logout' in navbar_content:
            print("   ✅ Navbar login/logout FOUND")
            checks.append(True)
        else:
            print("   ❌ Navbar login/logout NOT FOUND")
            checks.append(False)
else:
    print("   ❌ navbar.html not found")
    checks.append(False)

# Summary
print("\n" + "=" * 60)
print("VERIFICATION SUMMARY")
print("=" * 60)
passed = sum(checks)
total = len(checks)
print(f"\n✅ Passed: {passed}/{total} checks")
print(f"❌ Failed: {total - passed}/{total} checks")

if passed == total:
    print("\n🎉 ALL CHANGES VERIFIED! All features are implemented.")
    print("\n⚠️  IMPORTANT: Make sure to:")
    print("   1. Restart Flask server (python app.py)")
    print("   2. Clear browser cache or use incognito mode")
    print("   3. Test the features by visiting the URLs")
else:
    print(f"\n⚠️  {total - passed} check(s) failed. Please review the output above.")
print("=" * 60)

