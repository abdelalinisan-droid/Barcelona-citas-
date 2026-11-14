import os
import requests
from playwright.sync_api import sync_playwright

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
        response = requests.post(url, json=payload, timeout=10)
        print(f"Telegram response status: {response.status_code}")
    except Exception as e:
        print(f"Error sending telegram: {e}")

def check_and_book():
    print("Starting auto-booking check for Barcelona...")
    send_telegram_message("🤖 *Bot started execution...*")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 1. Open official website & select Barcelona
            print("Navigating to ICP website...")
            page.goto("https://icp.administracionespublicas.gob.es/icp/index.jsp", timeout=60000)
            
            print("Selecting province Barcelona...")
            page.wait_for_selector("#ce", timeout=20000)
            page.select_option("#ce", "08")
            page.click("#btnAceptar")
            page.wait_for_timeout(5000) # Safe wait avoiding networkidle freeze
            
            send_telegram_message("✅ *Step 1:* Province Barcelona selected successfully!")
            
            # 2. Select Service (Toma de huellas)
            print("Selecting service...")
            page.wait_for_selector("#tramite", timeout=20000)
            page.select_option("#tramite", index=1)
            page.click("#btnAceptar")
            page.wait_for_timeout(5000)
            
            send_telegram_message("✅ *Step 2:* Service selected successfully!")
            
            # 3. Fill Credentials securely
            if USER_NIE and USER_NAME:
                print("Filling credentials...")
                page.wait_for_selector("#txtIden", timeout=20000)
                page.fill("#txtIden", USER_NIE)
                page.fill("#txtNombreApellidos", USER_NAME)
                
                send_telegram_message("👤 *Step 3:* Credentials (NIE & Name) filled securely!")
            
        except Exception as e:
            err_msg = f"❌ *Error:* {str(e)[:150]}"
            print(err_msg)
            send_telegram_message(err_msg)
        finally:
            browser.close()

if __name__ == "__main__":
    check_and_book()
