import streamlit as st
import feedparser
import urllib.request
import ssl
import json
import pandas as pd
from datetime import date

# --- 1. BYPASS BLOCKS ---
ssl._create_default_https_context = ssl._create_unverified_context

# High-level headers to look like a real browser in India
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/rss+xml, text/xml, */*'
}

SOURCES = {
    "PIB - National": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1",
    "LiveMint - Economy": "https://www.livemint.com/rss/economy",
    "The Guardian - Tech": "https://www.theguardian.com/technology/rss"
}

# --- 2. THE LIVE ENGINE ---
st.set_page_config(page_title="UPSC Live Vault", layout="wide")
st.title("🎯 UPSC Strategic Vault: Live & Archived")

def fetch_live_news():
    daily_data = {}
    for name, url in SOURCES.items():
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as response:
                feed = feedparser.parse(response.read())
                if feed.entries:
                    daily_data[name] = [{"title": e.title, "link": e.link} for e in feed.entries[:5]]
        except Exception as e:
            st.sidebar.error(f"Error fetching {name}: {str(e)}")
    return daily_data

# --- 3. PERSISTENCE LOGIC ---
# We use st.session_state as a temporary cache and File Download as the permanent backup
if 'archive' not in st.session_state:
    st.session_state.archive = {}

if st.button("🔄 Fetch & Archive Today's News"):
    today_news = fetch_live_news()
    today_str = str(date.today())
    st.session_state.archive[today_str] = today_news
    st.success(f"Fetched news for {today_str}!")

# --- 4. DISPLAY & DOWNLOAD ---
selected_date = st.date_input("View Archive for:", date.today())
view_date = str(selected_date)

if view_date in st.session_state.archive:
    news_content = st.session_state.archive[view_date]
    cols = st.columns(len(news_content))
    for i, (source, articles) in enumerate(news_content.items()):
        with cols[i]:
            st.subheader(source)
            for art in articles:
                st.markdown(f"🔗 [{art['title']}]({art['link']})")
else:
    st.info("No data for this date in current session. Fetch today's news or upload archive.")

# --- 5. THE "NEVER LOSE DATA" BUTTON ---
st.sidebar.divider()
st.sidebar.subheader("📥 Permanent Backup")
if st.session_state.archive:
    json_data = json.dumps(st.session_state.archive, indent=4)
    st.sidebar.download_button(
        "Download Full Archive (JSON)",
        data=json_data,
        file_name="upsc_master_archive.json",
        mime="application/json"
    )

uploaded_file = st.sidebar.file_uploader("Upload Master Archive to Restore", type="json")
if uploaded_file:
    st.session_state.archive = json.load(uploaded_file)
    st.sidebar.success("Archive Restored!")
