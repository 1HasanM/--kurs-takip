import requests
from bs4 import BeautifulSoup
import json
import os
import time

URL = "https://tvgfbf.gov.tr/vucut-gelistirme-duyurulari"

KEYWORDS = [
    "kademe",
    "1. kademe",
    "antrenör",
    "kurs"
]

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    )
}


def send_message(message):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": message
            },
            timeout=30
        )

        print("BOT TOKEN:", BOT_TOKEN[:10] + "...")
        print("CHAT ID:", CHAT_ID)
        print("STATUS:", r.status_code)
        print("RESPONSE:", r.text)

    except Exception as e:
        print("Telegram gönderim hatası:", e)


def get_page():
    for attempt in range(3):
        try:
            print(f"Deneme {attempt+1}/3")
            response = requests.get(
                URL,
                headers=HEADERS,
                timeout=60
            )
            response.raise_for_status()
            return response.text

        except Exception as e:
            print(f"Hata: {e}")

            if attempt < 2:
                print("10 saniye bekleniyor...")
                time.sleep(10)
            else:
                return None


html = get_page()

if html is None:
    print("Siteye erişilemedi.")
    exit(0)

soup = BeautifulSoup(html, "html.parser")

announcements = []

for a in soup.find_all("a", href=True):
    title = a.get_text(strip=True)
    href = a["href"]

    if not title or len(title) < 5:
        continue

    lower = title.lower()

    if any(k in lower for k in KEYWORDS):

        if href.startswith("/"):
            href = "https://tvgfbf.gov.tr" + href

        announcements.append({
            "title": title,
            "url": href
        })

try:
    with open("seen.json", "r", encoding="utf-8") as f:
        seen = json.load(f)
except:
    seen = []

new_items = []

for item in announcements:
    if item["url"] not in seen:
        new_items.append(item)
        seen.append(item["url"])

if new_items:
    message = "🚨 TVGFBF'de yeni duyuru bulundu:\n\n"

    for item in new_items:
        message += f"• {item['title']}\n"
        message += f"{item['url']}\n\n"

    send_message(message)
    print("Telegram bildirimi gönderildi.")

else:
    print("Yeni duyuru yok.")

with open("seen.json", "w", encoding="utf-8") as f:
    json.dump(seen, f, ensure_ascii=False, indent=2)

print("Kontrol tamamlandı.")
