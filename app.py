import streamlit as st
import feedparser
import os
import json
import urllib.request
import ssl
from datetime import date

# --- 1. BYPASS SSL & SET HEADERS ---
# This fixes "Certificate Verify Failed" errors common on Gov sites
ssl._create_default_https_context = ssl._create_unverified_context

# Professional Browser Headers to bypass 403 Forbidden
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

# --- 2. SETUP ---
if not os.path.exists("Archive"): 
    os.makedirs("Archive")

SOURCES = {
    "PIB - National": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1",
    "PMO - Press Releases": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
    "DD News - राष्ट्रीय": "https://ddnews.gov.in/en/category/national/feed/",
    "The Guardian - World": "https://www.theguardian.com/world/rss",
    "The Guardian - Tech": "https://www.theguardian.com/technology/rss",
    "PRS India - Policy": "https://prsindia.org/theprsblog/feed",
    "LiveMint - Economy": "https://www.livemint.com/rss/economy"
}

# --- 3. UI ---
st.set_page_config(page_title="UPSC Strategic Vault", layout="wide", page_icon="🎯")
st.sidebar.title("📑 News Vault")
selected_date = st.sidebar.date_input("Revision Date", date.today())

# --- 4. ENGINE ---
st.title(f"Strategic Digest: {selected_date}")
archive_file = f"Archive/{selected_date}.json"
display_news = {}

if selected_date == date.today():
    for name, url in SOURCES.items():
        try:
            # Create a sophisticated request
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read()
                feed = feedparser.parse(content)
            
            if feed.entries:
                display_news[name] = [{"title": e.title, "link": e.link} for e in feed.entries[:8]]
            else:
                st.sidebar.error(f"Empty: {name} (Feed source has no entries today)")
        except Exception as e:
            # This will now tell you EXACTLY why it failed (e.g., 403 Forbidden)
            st.sidebar.warning(f"⚠️ {name}: {str(e)}")

    if display_news:
        with open(archive_file, "w", encoding='utf-8') as f: 
            json.dump(display_news, f, ensure_ascii=False)
            
elif os.path.exists(archive_file):
    with open(archive_file, "r", encoding='utf-8') as f: 
        display_news = json.load(f)
else:
    st.info("No archive found for this date. Check your sidebar for live errors.")

# --- 5. DISPLAY ---
if display_news:
    col1, col2 = st.columns(2)
    source_names = list(display_news.keys())
    for i, name in enumerate(source_names):
        with (col1 if i % 2 == 0 else col2):
            st.subheader(name)
            for art in display_news[name]:
                st.markdown(f"📍 [{art['title']}]({art['link']})")
            st.divider()
