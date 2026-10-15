"""
verify_live_service.py
Automated smoke & health verification probe for MAKITEST deployment.
Checks landing page, static assets, CSRF protection, and administrator authentication.
"""

import os
import sys
import re
import urllib.request
import urllib.parse
from http.cookiejar import CookieJar

DEFAULT_URL = "https://new-makitest-web-app-analytics-test-736992802574.asia-east1.run.app"
BASE_URL = os.environ.get("SERVICE_URL", DEFAULT_URL).rstrip("/")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "MakitestAdmin2026!")

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

print("=" * 60)
print(f"MAKITEST Smoke & Health Verification Probe")
print(f"Target: {BASE_URL}")
print("=" * 60)

failures = []

def run_check(step_name, func):
    try:
        func()
        print(f"[PASS] {step_name}")
    except Exception as e:
        print(f"[FAIL] {step_name}: {e}")
        failures.append((step_name, str(e)))

# Check 1: Landing Page
def check_landing_page():
    req = urllib.request.Request(f"{BASE_URL}/", headers={"User-Agent": "MakitestVerifier/1.0"})
    with opener.open(req, timeout=15) as resp:
        assert resp.getcode() == 200, f"Expected 200 OK, got {resp.getcode()}"
        html = resp.read().decode("utf-8")
        assert "MAKITEST" in html, "Page does not contain 'MAKITEST' branding"

# Check 2: Static Assets via WhiteNoise
def check_static_assets():
    css_url = f"{BASE_URL}/static/makitest/app.css"
    req = urllib.request.Request(css_url, headers={"User-Agent": "MakitestVerifier/1.0"})
    with opener.open(req, timeout=15) as resp:
        assert resp.getcode() == 200, f"Expected 200 OK, got {resp.getcode()}"
        content_type = resp.headers.get("Content-Type", "")
        assert "text/css" in content_type, f"Expected text/css, got {content_type}"

# Check 3: Signup Page and CSRF
def check_signup_page():
    req = urllib.request.Request(f"{BASE_URL}/signup/", headers={"User-Agent": "MakitestVerifier/1.0"})
    with opener.open(req, timeout=15) as resp:
        assert resp.getcode() == 200, f"Expected 200 OK, got {resp.getcode()}"
        html = resp.read().decode("utf-8")
        assert "Create Your Account" in html, "Page does not contain signup header"
        assert 'name="csrfmiddlewaretoken"' in html, "CSRF token input missing from form"

# Check 4: Login Page and Admin Authentication Flow
def check_admin_login():
    # 1. Fetch fresh CSRF token from login page
    login_url = f"{BASE_URL}/login/"
    req = urllib.request.Request(login_url, headers={"User-Agent": "MakitestVerifier/1.0"})
    with opener.open(req, timeout=15) as resp:
        assert resp.getcode() == 200, f"Expected 200 OK, got {resp.getcode()}"
        html = resp.read().decode("utf-8")
        match = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', html)
        assert match, "Could not extract CSRF token from login form"
        csrf_token = match.group(1)

    # 2. Submit credentials
    payload = urllib.parse.urlencode({
        "csrfmiddlewaretoken": csrf_token,
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
    }).encode("utf-8")

    post_req = urllib.request.Request(
        login_url,
        data=payload,
        headers={
            "Origin": BASE_URL,
            "Referer": login_url,
            "User-Agent": "MakitestVerifier/1.0",
        },
    )

    with opener.open(post_req, timeout=15) as resp:
        final_url = resp.geturl()
        assert resp.getcode() == 200, f"Expected 200 OK, got {resp.getcode()}"
        assert "/adminside/" in final_url, f"Expected redirect to /adminside/, got {final_url}"

# Execute checks
run_check("1. Landing Page Response (200 OK)", check_landing_page)
run_check("2. Static Asset Delivery via WhiteNoise (app.css)", check_static_assets)
run_check("3. Signup Page & CSRF Token Generation", check_signup_page)
run_check("4. Administrator Authentication & /adminside/ Redirection", check_admin_login)

print("=" * 60)
if failures:
    print(f"FAILED: {len(failures)} check(s) did not pass.")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED: Live service is healthy and operational!")
    sys.exit(0)
