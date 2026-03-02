import sys
from selenium import webdriver
options = webdriver.ChromeOptions()
options.debugger_address = "127.0.0.1:9222"
try:
    driver = webdriver.Chrome(options=options)
    print(f"URL: {driver.current_url}")
    print(f"TITLE: {driver.title}")
except Exception as e:
    print(f"Error: {e}")
