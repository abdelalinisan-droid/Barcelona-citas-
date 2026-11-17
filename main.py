import os
import time
from datetime import datetime, timezone, timedelta
import requests
from playwright.sync_api import sync_playwright

# Load environment variables and user credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
USER_NIE = os.getenv("USER_NIE")
USER_NAME = os.getenv("USER_NAME")
USER_PHONE = os.getenv("USER_PHONE", "647496372")
USER_EMAIL = os.getenv("USER_EMAIL", "omarbouaali742@gmail.com")
USER_COUNTRY = os.getenv("USER_COUNTRY", "España")

def send_telegram_message(message):
    """Send alert messages via Telegram bot with Markdown formatting"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending telegram message: {e}")

def check_barcelona_appointment(page):
    """Check appointment availability exclusively in Barcelona province"""
    try:
        print("Checking Barcelona offices for Toma de huellas...")
        
        # 1. Open website & select Barcelona province (08)
        page.goto("https://icp.administracionespublicas.gob.es/icp/index.jsp", timeout=60000)
        page.wait_for_selector("#ce", timeout=15000)
        page.select_option("#ce", "08")
        page.click("#btnAceptar")
        page.wait_for_timeout(2000)
        
        # 2. Select Fingerprinting service (Toma de huellas)
        page.wait_for_selector("#tramite", timeout=15000)
        page.select_option("#tramite", index=1)
        page.click("#btnAceptar")
        page.wait_for_timeout(2000)
        
        # 3. Fill user credentials securely (NIE and Name)
        if USER_NIE and USER_NAME:
            page.wait_for_selector("#txtIden", timeout=15000)
            page.fill("#txtIden", USER_NIE)
            page.fill("#txtNombreApellidos", USER_NAME)
            page.click("#btnAceptar")
            page.wait_for_timeout(3000)
        
        # 4. Analyze page content to determine slot status
        page_content = page.content().lower()
        
        if "no hay citas" in page_content or "en este momento" in page_content or "lo sentimos" in page_content:
            return False, ""
        else:
            try:
                result_text = page.locator("body").inner_text()
                snippet = result_text[:300].replace("\n", " ")
            except:
                snippet = "Available slots detected in Barcelona region!"
            return True, snippet
            
    except Exception as e:
        print(f"Check error: {e}")
        return False, ""

def run_barcelona_monitoring():
    """Smart continuous checking loop with high frequency"""
    print("Starting professional Barcelona monitoring bot (High Speed Mode)...")
    
    # توقيت إسبانيا المحلي (CET = UTC+1)
    spain_tz = timezone(timedelta(hours=1))
    now_spain = datetime.now(spain_tz)
    
    start_msg = f"🟢 *Bot Active (Fast Mode):* Monitoring ICP Barcelona appointments. (Spain Time: {now_spain.strftime('%H:%M')})"
    send_telegram_message(start_msg)
    
    start_time = time.time()
    max_duration = 28 * 60  # زيادة مدة الجلسة إلى 28 دقيقة لتقليل فجوات التوقف
    check_interval = 25     # تقليص وقت الانتظار بين الفحوصات إلى 25 ثانية فقط
    
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
            is_available, details = check_barcelona_appointment(page)
            
            if is_available:
                official_url = "https://icp.administracionespublicas.gob.es/icp/index.jsp"
                msg = (
                    f"🚨 *BINGO! APPOINTMENT AVAILABLE IN BARCELONA!* 🔥\n\n"
                    f"📄 *Office Details:* `{details[:200]}`\n\n"
                    f"📋 *Your Quick-Copy Info (Tap any to copy):*\n"
                    f"🆔 NIE: `{USER_NIE}`\n"
                    f"👤 Name: `{USER_NAME}`\n"
                    f"📞 Phone: `{USER_PHONE}`\n"
                    f"📧 Email: `{USER_EMAIL}`\n"
                    f"🌍 Country: `{USER_COUNTRY}`\n\n"
                    f"👉 [Click here to open official booking site instantly]({official_url})\n\n"
                    f"🏃‍♂️ *Hurry up and book before slots run out!*"
                )
                print(msg)
                send_telegram_message(msg)
                break
            else:
                print(f"No appointments in Barcelona. Waiting {check_interval}s...")
                time.sleep(check_interval)
                
        browser.close()

if __name__ == "__main__":
    run_barcelona_monitoring()
