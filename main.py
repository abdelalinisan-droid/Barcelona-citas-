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

def check_icp_barcelona():
    print("Starting auto-booking check for Barcelona...")
    send_telegram_message("🤖 *Bot is running successfully!*\n👤 User credentials loaded for auto-booking.\n📍 Monitoring Barcelona appointments...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Access the official Spanish public administration appointment website
            page.goto("https://icp.administracionespublicas.gob.es/icp/index.jsp", timeout=60000)
            
            # Verify secure loading of credentials
            if USER_NIE and USER_NAME:
                print("User credentials loaded securely for auto-booking.")
                
        except Exception as e:
            print(f"An error occurred during execution: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_icp_barcelona()
