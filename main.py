import os
import time
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
USER_NIE = os.getenv("USER_NIE")
USER_NAME = os.getenv("USER_NAME")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending telegram: {e}")

def check_appointment_once(page):
    try:
        # 1. Open website & select Barcelona
        page.goto("https://icp.administracionespublicas.gob.es/icp/index.jsp", timeout=60000)
        page.wait_for_selector("#ce", timeout=15000)
        page.select_option("#ce", "08")
        page.click("#btnAceptar")
        page.wait_for_timeout(2000)
        
        # 2. Select Service (Toma de huellas)
        page.wait_for_selector("#tramite", timeout=15000)
        page.select_option("#tramite", index=1)
        page.click("#btnAceptar")
        page.wait_for_timeout(2000)
        
        # 3. Fill Credentials securely
        if USER_NIE and USER_NAME:
            page.wait_for_selector("#txtIden", timeout=15000)
            page.fill("#txtIden", USER_NIE)
            page.fill("#txtNombreApellidos", USER_NAME)
            page.click("#btnAceptar")
            page.wait_for_timeout(3000)
        
        # 4. Check status
        page_content = page.content().lower()
        if "no hay citas" in page_content or "en este momento" in page_content or "lo sentimos" in page_content:
            return False # No appointments
        else:
            return True  # Appointments available or page changed!
            
    except Exception as e:
        print(f"Check iteration error: {e}")
        return False

def run_continuous_monitoring():
    print("Starting continuous appointment monitoring loop...")
    send_telegram_message("🔄 *Bot started continuous monitoring loop (checking every 40s)...*")
    
    start_time = time.time()
    max_duration = 24 * 60  # Run for 24 minutes per GitHub Action execution
    check_interval = 40     # Wait 40 seconds between each check
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        while time.time() - start_time < max_duration:
            is_available = check_appointment_once(page)
            
            if is_available:
                print("ALERT: Appointments available!")
                send_telegram_message("🚨 *URGENT:* Cita available right now in Barcelona! Go book it immediately! 🔥🏃‍♂️")
                break # Stop loop to grab attention
            else:
                print("No appointments found in this check. Waiting...")
                time.sleep(check_interval)
                
        browser.close()

if __name__ == "__main__":
    run_continuous_monitoring()
