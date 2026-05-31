#!/usr/bin/env python3
"""
Simple Selenium script to load a webpage using webdriver-manager.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def main():
    # Chrome options for headless mode
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    # Auto-download correct chromedriver version
    service = Service(ChromeDriverManager().install())

    # Launch browser
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Load webpage
        driver.get('https://www.google.com')
        print(f'✅ SUCCESS: {driver.title}')
    except Exception as e:
        print(f'❌ ERROR: {e}')
    finally:
        driver.quit()


if __name__ == '__main__':
    main()