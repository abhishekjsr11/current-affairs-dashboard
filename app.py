import streamlit as st
import feedparser
import urllib.request
import ssl
import json
import re
from datetime import date

# 1. BOT-BYPASS & SECURITY
ssl._create_default_https_context = ssl._create_unverified_context

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive'
}

# 2. THE COMPLETE 2026 UPSC SOURCE LIST
SOURCES = {
    "PIB - National": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1",
    "PMO - Press Releases": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
    "PRS India - Policy Blog": "https://prsindia.org/theprsblog/feed",
    "DD News - National": "https://ddnews.gov.in/en/category/national/feed/",
    "LiveMint - Economy": "https://www.livemint.com/rss/economy",
    "Guardian - International": "https://www.theguardian.com/world/rss",
    "Guardian - Science & Tech": "https://www.theguardian.com/technology/rss"
}

# 3. UPSC KEYWORD HIGHLIGHTER
UPSC_KEYWORDS = ["Inflation", "GDP", "RBI", "Constitution", "Supreme Court", "ISRO", "Digital India", "Green Hydrogen", "Quantum", "Semiconductor", "Bill", "Act", "ASEAN", "G20"]

def highlight_keywords(text):
    for word in UPSC_KEYWORDS:
        # Case-insensitive bolding
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        text = pattern.sub(f"**{word}**", text)
    return text

# 4. UI CONFIG
st.set_page_config(page_title="UPSC Strategic Vault", layout="wide", page_icon="🎯")
st.title("🛰️ UPSC Strategic Vault: 2026 Live Portal")

if 'master_vault' not in st.session_state:
    st.session_state.master_vault = {}

# 5. FETCH ENGINE
def secure_fetch_all():
    results = {}
    bar = st.sidebar.progress(0)
    for i, (name, url) in enumerate(SOURCES.items()):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as response:
                feed = feedparser.parse(response.read())
            if feed.entries:
                results[name] = [{"title": e.title, "link": e.link} for e in feed.entries[:7]]
        except Exception as e:
            st.sidebar.warning(f"⚠️ {name} Blocked/Delayed")
        bar.progress((i + 1) / len(SOURCES))
    return results

# 6. SIDEBAR CONTROLS
st.sidebar.header("📂 Archive Management")
today_str = str(date.today())

if st.sidebar.button("🚀 Fetch Today's Live Data"):
    with st.spinner("Accessing National & Global Feeds..."):
        daily_data = secure_fetch_all()
        if daily_data:
            st.session_state.master_vault[today_str] = daily_data
            st.sidebar.success(f"Archived for {today_str}")

# Master Persistence
st.sidebar.divider()
if st.session_state.master_vault:
    js_data = json.dumps(st.session_state.master_vault, indent=4)
    st.sidebar.download_button("💾 Download Master Archive", js_data, f"UPSC_Vault_{today_str}.json")

upl_vault = st.sidebar.file_uploader("📂 Restore/Upload Archive", type="json")
if upl_vault:
    st.session_state.master_vault = json.load(upl_vault)
    st.sidebar.success("Vault Restored!")

# 7. MAIN DISPLAY
selected_date = st.date_input("Revision Date:", date.today())
view_date = str(selected_date)

if view_date in st.session_state.master_vault:
    data = st.session_state.master_vault[view_date]
    col1, col2 = st.columns(2)
    source_names = list
