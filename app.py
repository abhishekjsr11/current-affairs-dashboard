import ssl
ssl._create_default_https_context = ssl._create_unverified_contextimport streamlit as st
import feedparser
import os
import json
import urllib.request
from datetime import date

# --- 1. SETUP ---
if not os.path.exists("Archive"): 
    os.makedirs("Archive")

# 2026 Sources: National (Bilingual) + Global Tech & Economy
SOURCES = {
    "PIB - National (Bilingual)": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1",
    "PMO - Press Releases": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
    "DD News - राष्ट्रीय समाचार": "https://ddnews.gov.in/en/category/national/feed/",
    "The Guardian - International": "https://www.theguardian.com/world/rss",
    "The Guardian - Science & Tech": "https://www.theguardian.com/technology/rss", # NEW
    "PRS India - Policy Blog": "https://prsindia.org/theprsblog/feed",
    "LiveMint - Economy": "https://www.livemint.com/rss/economy"
}

# --- 2. UI CONFIG ---
st.set_page_config(page_title="UPSC Strategic Vault", layout="wide", page_icon="🎯")
st.sidebar.title("📑 News Vault")
selected_date = st.sidebar.date_input("Revision Date", date.today())

# --- 3. ARCHIVE ENGINE ---
st.title(f"Strategic Digest: {selected_date}")
archive_file = f"Archive/{selected_date}.json"
display_news = {}

if selected_date == date.today():
    for name, url in SOURCES.items():
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                feed = feedparser.parse(response.read())
            if feed.entries:
                display_news[name] = [{"title": e.title, "link": e.link} for e in feed.entries[:8]]
        except:
            st.sidebar.warning(f"Note: {name} refresh delayed.")
    
    if display_news:
        with open(archive_file, "w", encoding='utf-8') as f: 
            json.dump(display_news, f, ensure_ascii=False)
            
elif os.path.exists(archive_file):
    with open(archive_file, "r", encoding='utf-8') as f: 
        display_news = json.load(f)
else:
    st.info("No data for this date. Your bilingual archive starts today!")

# --- 4. DISPLAY ---
if display_news:
    col1, col2 = st.columns(2)
    source_names = list(display_news.keys())
    for i, name in enumerate(source_names):
        with (col1 if i % 2 == 0 else col2):
            st.subheader(name)
            for art in display_news[name]:
                st.markdown(f"📍 [{art['title']}]({art['link']})")
            st.divider()

st.sidebar.success("Guardian Science & Tech Integrated.")
