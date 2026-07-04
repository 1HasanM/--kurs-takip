import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://tvgfbf.gov.tr/vucut-gelistirme-duyurulari"

KEYWORDS = [
    "kademe",
    "1. kademe",
    "antrenör",
    "kurs"
]

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_message(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )


r = requests.get(URL, timeout=20)
soup = BeautifulSoup(r.text, "html.parser")

titles = []

for a in soup.find_all("a"):
    text = a.get_text(strip=True)
    if text:
        titles.append(text)

try:
    with open("seen.json", "r", encoding="utf-8") as f:
        seen = json.load(f)
except:
    seen = []

new_items = []

for title in titles:
    lower = title.lower()

    if any(k in lower for k in KEYWORDS):
        if title not in seen:
            new_items.append(title)
            seen.append(title)

if new_items:
    msg = "🚨 Yeni TVGFBF duyurusu:\n\n"
    msg += "\n".join(new_items)
    msg += f"\n\n{URL}"

    send_message(msg)

with open("seen.json", "w", encoding="utf-8") as f:
    json.dump(seen, f, ensure_ascii=False)
