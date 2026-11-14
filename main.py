import os
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram_message(message):
  if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("Telegram tokens not set!")
    return
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
  try:
    response = requests.post(url, json=payload)
    print(f"Telegram response: {response.text}")
  except Exception as e:
    print(f"Error sending telegram: {e}")


def check_icp_barcelona():
  print("Starting ICP Barcelona check...")

  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    try:
      page.goto(
          "https://icp.administracionespublicas.gob.es/icp/index.jsp",
          timeout=60000,
      )
      print("Page loaded successfully.")
      title = page.title()
      print(f"Page Title: {title}")
    except Exception as e:
      print(f"Error navigating to ICP: {e}")
    finally:
      browser.close()


if __name__ == "__main__":
  check_icp_barcelona()
