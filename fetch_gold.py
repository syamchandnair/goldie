import csv
import re
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup

URL = "https://www.pngjewellers.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_rates():
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Target the metal pricing popup, falling back to full page text if class changes
    popup = soup.find("div", class_=re.compile("metal-pricing-popup", re.I)) or soup
    text = popup.get_text(" ", strip=True)

    rate_24k = re.search(r"24K\s*Gold\s*₹?\s*([\d,]+)", text, re.I)
    rate_22k = re.search(r"22K\s*Gold\s*₹?\s*([\d,]+)", text, re.I)

    return (
        rate_24k.group(1).replace(",", "") if rate_24k else "N/A",
        rate_22k.group(1).replace(",", "") if rate_22k else "N/A",
    )

if __name__ == "__main__":
    ist = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")
    gold_24k, gold_22k = fetch_rates()

    with open("gold_rates.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([now_ist, gold_24k, gold_22k])

    print(f"[{now_ist}] 24K: ₹{gold_24k}, 22K: ₹{gold_22k}")
