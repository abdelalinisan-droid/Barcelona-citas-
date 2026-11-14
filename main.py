import os
import time
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
USER_NIE = os.getenv("USER_NIE")
USER_NAME = os.getenv("USER_NAME")

# Complete list of all Spanish provinces with their official ICP codes
SPAIN_PROVINCES = [
    {"code": "01", "name": "Álava"},
    {"code": "02", "name": "Albacete"},
    {"code": "03", "name": "Alicante"},
    {"code": "04", "name": "Almería"},
    {"code": "05", "name": "Ávila"},
    {"code": "06", "name": "Badajoz"},
    {"code": "07", "name": "Illes Balears"},
    {"code": "08", "name": "Barcelona"},
    {"code": "09", "name": "Burgos"},
    {"code": "10", "name": "Cáceres"},
    {"code": "11", "name": "Cádiz"},
    {"code": "12", "name": "Castellón"},
    {"code": "13", "name": "Ciudad Real"},
    {"code": "14", "name": "Córdoba"},
    {"code": "15", "name": "A Coruña"},
    {"code": "16", "name": "Cuenca"},
    {"code": "17", "name": "Girona"},
    {"code": "18", "name": "Granada"},
    {"code": "19", "name": "Guadalajara"},
    {"code": "20", "name": "Gipuzkoa"},
    {"code": "21", "name": "Huelva"},
    {"code": "22", "name": "Huesca"},
    {"code": "23", "name": "Jaén"},
    {"code": "24", "name": "León"},
    {"code": "25", "name": "Lleida"},
    {"code": "26", "name": "La Rioja"},
    {"code": "27", "name": "Lugo"},
    {"code": "28", "name": "Madrid"},
    {"code": "29", "name": "Málaga"},
    {"code": "30", "name": "Murcia"},
    {"code": "31", "name": "Navarra"},
    {"code": "32", "name": "Ourense"},
    {"code": "33", "name": "Asturias"},
    {"code": "34", "name": "Palencia"},
    {"code": "35", "name": "Las Palmas"},
    {"code": "36", "name": "Pontevedra"},
    {"code": "37", "name": "Salamanca"},
    {"code": "38", "name": "Santa Cruz de Tenerife"},
    {"code": "39", "name": "Cantabria"},
    {"code": "40", "name": "Segovia"},
    {"code": "41", "name": "Sevilla"},
    {"code": "42", "name": "Soria"},
    {"code": "43", "name": "Tarragona"},
    {"code": "44", "name": "Teruel"},
    {"code": "45", "name": "Toledo"},
    {"code": "46", "name": "Valencia"},
    {"code": "47", "name": "Valladolid"},
    {"code": "48", "name": "Vizcaya"},
    {"code": "49", "name": "Zamora"},
    {"code": "50", "name": "Zaragoza"},
    {"code": "51", "name": "Ceuta"},
    {"code": "52", "name": "Melilla"}
]

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

def check_province(page, prov):
    try:
        prov_code = prov["code"]
        prov_name = prov["name"]
        
        print(f"Scanning province: {prov_name} ({prov_code})")
        
        # 1. Open website & select province
        page.goto("https://icp.administracionespublicas.gob.es/icp/index.jsp", timeout=60000)
        page.wait_for_selector("#ce", timeout=12000)
        page.select_option("#ce", prov_code)
        page.click("#btnAceptar")
        page.wait_for_timeout(1500)
        
        # 2. Select Service (Toma de huellas)
        page.wait_for_selector("#tramite", timeout=12000)
        page.select_option("#tramite", index=1)
        page.click("#btnAceptar")
        page.wait_for_timeout(1500)
        
        # 3. Fill Credentials securely
        if USER_NIE and USER_NAME:
            page.wait_for_selector("#txtIden", timeout=12000)
            page.fill("#txtIden", USER_NIE)
            page.fill("#txtNombreApellidos", USER_NAME)
            page.click("#btnAceptar")
            page.wait_for_timeout(2500)
        
        # 4. Check status
        page_content = page.content().lower()
        if "no hay citas" in page_content or "en este momento" in page_content or "lo sentimos" in page_content:
            return False
        else:
            return True # Available!
            
    except Exception as e:
        print(f"Error checking {prov['name']}: {e}")
        return False

def run_all_spain_monitoring():
    print("Starting All-Spain scanning loop...")
    send_telegram_message("🇪🇸 *Bot started scanning ALL of Spain (52 provinces)... Let's hunt for a Cita! 🕵️‍♂️*")
    
    start_time = time.time()
    max_duration = 23 * 60  # Run for 23 minutes per GitHub Action execution
    
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
            for prov in SPAIN_PROVINCES:
                # Break loop if approaching time limit
                if time.time() - start_time >= max_duration:
                    break
                    
                is_available = check_province(page, prov)
                
                if is_available:
                    msg = f"🚨 *BINGO!* Cita available in *{prov['name']}*! Go check immediately! 🔥🏃‍♂️"
                    print(msg)
                    send_telegram_message(msg)
                
                # Brief pause between provinces to keep it safe and stable
                time.sleep(5)
                
            # Rest a bit after finishing a full sweep of Spain before starting the next round
            print("Completed full Spain sweep. Waiting before next round...")
            time.sleep(20)
                
        browser.close()

if __name__ == "__main__":
    run_all_spain_monitoring()
