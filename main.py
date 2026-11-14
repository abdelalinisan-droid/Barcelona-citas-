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
    print("Starting automated appointment check for Barcelona...")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()
            
            # 1. Open official website & select Barcelona
            page.goto("https://icp.administracionespublicas.gob.es/icp/index.jsp", timeout=60000)
            page.wait_for_selector("#ce", timeout=25000)
            page.select_option("#ce", "08")
            page.click("#btnAceptar")
            page.wait_for_timeout(3000)
            
            # 2. Select Service (Toma de huellas)
            page.wait_for_selector("#tramite", timeout=25000)
            page.select_option("#tramite", index=1)
            page.click("#btnAceptar")
            page.wait_for_timeout(3000)
            
            # 3. Fill Credentials securely
            if USER_NIE and USER_NAME:
                page.wait_for_selector("#txtIden", timeout=25000)
                page.fill("#txtIden", USER_NIE)
                page.fill("#txtNombreApellidos", USER_NAME)
                
                # Click submit button to check appointments page
                page.click("#btnAceptar")
                page.wait_for_timeout(5000)
            
            # 4. Check appointment availability on the resulting page
            page_content = page.content().lower()
            
            if "no hay citas" in page_content or "en este momento" in page_content or "lo sentimos" in page_content:
                print("Status: No appointments available right now.")
                # We don't spam Telegram when there are no appointments, 
                # but you can uncomment the line below if you want a notification every time it checks:
                # send_telegram_message("🔍 *Bot checked:* No appointments available currently.")
            else:
                print("ALERT: Appointments might be available!")
                send_telegram_message("🚨 *URGENT:* Cita available or page changed in Barcelona! Check immediately! 🔥")
            
            browser.close()
            
        except Exception as e:
            err_msg = f"❌ *Execution Error:* {str(e)[:180]}"
            print(err_msg)
            send_telegram_message(err_msg)

if __name__ == "__main__":
    check_and_book()
