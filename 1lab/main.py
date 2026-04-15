import requests
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime

urls = {
    "habr": "https://habr.com/ru/rss/all/all/?fl=ru",
    "techcrunch": "https://techcrunch.com/feed/"
}

def get_data(url):
    return requests.get(url).text

def parse_rss(xml_data, source):
    root = ET.fromstring(xml_data)
    items = []

    for item in root.findall(".//item"):
        title = item.find("title").text if item.find("title") is not None else ""
        link = item.find("link").text if item.find("link") is not None else ""
        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
        category = item.find("category").text if item.find("category") is not None else ""

        try:
            date = datetime.strptime(pub_date[:25], "%a, %d %b %Y %H:%M:%S")
        except:
            date = None

        items.append({
            "title": title.strip(),
            "url": link.strip(),
            "date": str(date),
            "source": source,
            "category": category.strip()
        })

    return items

def save_to_db(data):
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT UNIQUE,
            date TEXT,
            source TEXT,
            category TEXT
        )
    """)

    for i in data:
        try:
            cur.execute(
                "INSERT INTO items (title, url, date, source, category) VALUES (?, ?, ?, ?, ?)",
                (i["title"], i["url"], i["date"], i["source"], i["category"])
            )
        except:
            pass

    conn.commit()
    conn.close()

def show_table():
    conn = sqlite3.connect("news.db")
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT title, source, category, date
        FROM items
        ORDER BY date DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    print("\n" + "="*100)
    print(f"{'TITLE':40} | {'SOURCE':10} | {'CATEGORY':15} | DATE")
    print("="*100)

    for r in rows:
        title = (r[0][:37] + "...") if len(r[0]) > 40 else r[0]
        print(f"{title:40} | {r[1]:10} | {r[2]:15} | {r[3]}")

    print("="*100)

all_data = []

for name, url in urls.items():
    raw = get_data(url)
    all_data.extend(parse_rss(raw, name))

save_to_db(all_data)

print("Готово! Записей:", len(all_data))
show_table()
