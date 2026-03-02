import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.debugger_address = "127.0.0.1:9222"

try:
    driver = webdriver.Chrome(options=options)
    
    driver.get("http://localhost:3000/login")
    time.sleep(2)
    
    driver.execute_script("window.localStorage.clear();")
    driver.get("http://localhost:3000/login")
    time.sleep(2)
    
    driver.execute_script("""
        const emailInput = document.querySelector('input[type="email"]');
        emailInput.value = 'admin@valuadis.com';
        emailInput.dispatchEvent(new Event('input', { bubbles: true }));
        
        const passInput = document.querySelector('input[type="password"]');
        passInput.value = 'password123';
        passInput.dispatchEvent(new Event('input', { bubbles: true }));
        
        const form = document.querySelector('form');
        form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    """)
    
    time.sleep(3)
    
    print(f"URL: {driver.current_url}")
    print("\nBrowser Logs:")
    for log in driver.get_log('browser'):
        print(f"{log['level']}: {log['message']}")
        
    print(f"\nToken in localStorage: {driver.execute_script('return window.localStorage.getItem(`valuadis_token`)')}")
    
except Exception as e:
    print(f"Error: {e}")
