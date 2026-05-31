#!/usr/bin/env python3
"""
Shoonya OAuth authentication using Selenium + webdriver-manager.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException
from urllib.parse import urlparse, parse_qs
import pyotp
import time
import json


# ─── CONFIG ───────────────────────────────────────────────────────────────────────
# Replace with your actual credentials
CLIENT_ID   = "FA333160_U"
USER_ID     = "FA333160"
PASSWORD    = "Taknev80####"  # Update with actual password
TOTP_SECRET = "74GC2ZH5Q54SY2RFF2GLLSKTFZ754Z6D"  # From cred.yml
LOGIN_URL   = f"https://trade.shoonya.com/OAuthlogin/investor-entry-level/login?api_key={CLIENT_ID}&route_to=abc"
TOKEN_URL   = "https://trade.shoonya.com/NorenWClientAPI/GenAcsTok"


def scan_network_for_code(driver):
    """Scan browser logs for OAuth code."""
    try:
        logs = driver.get_log("performance")
        for entry in logs:
            try:
                message = json.loads(entry["message"])["message"]
                if message.get("method") == "Network.requestWillBeSent":
                    url = message.get("params", {}).get("request", {}).get("url", "")
                    if "code=" in url and "shoonya" in url.lower():
                        parsed = urlparse(url)
                        code = parse_qs(parsed.query).get("code", [None])[0]
                        if code:
                            return code
            except Exception:
                continue
    except Exception:
        pass
    return None


def fast_fill(driver, element, value):
    """Fill input field quickly."""
    element.click()
    time.sleep(0.1)
    element.clear()
    element.send_keys(value)
    time.sleep(0.1)


# ─── Chrome HEADLESS with webdriver-manager ─────────────────────────────────
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 30)

auth_code = None

try:
    # ── Step 1: Login and capture auth code ─────────────────────────────────────
    print("Logging in to Shoonya (background)...")
    driver.get(LOGIN_URL)

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']")))
    time.sleep(1)

    all_inputs = driver.find_elements(By.CSS_SELECTOR, "input:not([type='hidden']):not([type='checkbox']):not([type='radio'])")
    visible_inputs = [inp for inp in all_inputs if inp.is_displayed()]

    fast_fill(driver, visible_inputs[0], USER_ID)
    fast_fill(driver, visible_inputs[1], PASSWORD)

    if TOTP_SECRET:
        otp_value = pyotp.TOTP(TOTP_SECRET).now()
        fast_fill(driver, visible_inputs[2], otp_value)

    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='LOGIN']"))).click()
    print("Credentials submitted. Capturing auth code...")

    start = time.time()
    while True:
        auth_code = scan_network_for_code(driver)

        if auth_code:
            print(f"✅ Auth Code: {auth_code}")
            break

        if time.time() - start > 60:
            if TOTP_SECRET:
                new_otp = pyotp.TOTP(TOTP_SECRET).now()
                if new_otp != otp_value:
                    fast_fill(driver, visible_inputs[2], new_otp)
                    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='LOGIN']"))).click()
                    start = time.time()
                    otp_value = new_otp
                    continue
            print("[TIMEOUT] Could not capture auth code.")
            break

        time.sleep(0.5)

except (InvalidSessionIdException, WebDriverException) as e:
    print(f"[ERROR] Browser issue: {e}")
except Exception as e:
    print(f"[ERROR] {e}")
finally:
    try:
        driver.quit()
    except Exception:
        pass