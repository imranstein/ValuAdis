import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.debugger_address = "127.0.0.1:9222"

try:
    driver = webdriver.Chrome(options=options)
    driver.get("http://localhost:3000/login")
    time.sleep(2)
    
    # Run the exact fetch the frontend runs
    res = driver.execute_script("""
        return fetch('http://localhost:8020/api/v1/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email: 'admin@valuadis.com', password: 'password123'})
        }).then(async r => {
            if (!r.ok) {
                const text = await r.text();
                return `Error ${r.status}: ${text}`;
            }
            return await r.json();
        }).catch(e => `Fetch exception: ${e.message}`);
    """)
    print(f"Fetch result: {res}")
    
except Exception as e:
    print(f"Error: {e}")
