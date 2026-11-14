import os
import requests
from playwright.sync_api import sync_playwright

# Read secure environment variables safely
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
USER_NIE = os.getenv("USER_NIE")
USER_NAME = os.getenv("USER_NAME")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram tokens not set!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Telegram response: {response.status_code}")
    except Exception as e:
        print(f"Error sending telegram: {e}")

def check_and_book():
    print("Starting auto-booking check for Barcelona...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 1. Open the official Spanish public administration appointment website
            page.goto("https://icp.administracionespublicas.gob.es/icp/index.jsp", timeout=60000)
            
            # 2. Select Province (Barcelona = 08)
            page.wait_for_selector("#ce", timeout=10000)
            page.select_option("#ce", "08")
            page.click("#btnAceptar")
            page.wait_for_load_state("networkidle")
            
            send_telegram_message("✅ *Step 1:* Province Barcelona selected successfully!")
            
            # 3. Select Service (Toma de huellas / Fingerprints)
            # Note: Selectors can be adjusted based on the specific dropdown option value for Toma de huellas
            page.wait_for_selector("#tramite", timeout=10000)
            # Usually, Toma de huellas corresponds to a specific value like policia or certinicados, let's select by label or value
            page.select_option("#tramite", index=1) # Or specific value
            page.click("#btnAceptar")
            page.wait_for_load_state("networkidle")
            
            send_telegram_message("✅ *Step 2:* Service selected successfully!")
            
            # 4. Fill User Credentials securely
            if USER_NIE and USER_NAME:
                print("Filling user credentials...")
                # Filling NIE / Document number
                page.fill("#txtIden", USER_NIE)
                # Filling Name and Surname
                page.fill("#txtNombreApellidos", USER_NAME)
                
                send_telegram_message(f"👤 *Credentials Loaded:* NIE and Name filled securely for auto-booking.")
            
        except Exception as e:
            error_msg = f"❌ *Error during execution:* {str(e)}"
            print(error_msg)
            send_telegram_message(error_msg)
        finally:
            browser.close()

if __name__ == "__main__":
    check_and_book()
