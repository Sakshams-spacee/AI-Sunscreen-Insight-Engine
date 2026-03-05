import streamlit as st
import requests
import pandas as pd
import altair as alt

# -------------------------
# Reddit Fetch Function (Public JSON Version)
# -------------------------

def fetch_reddit_posts(query):
    subreddits = [
        "IndianSkincareAddicts",
        "skincareaddictsindia",
        "IndianBeautyTalks"
    ]

    # We use a generic browser-like User-Agent to avoid the '429' (Too Many Requests) error
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    posts = []

    for sub in subreddits:
        # We append .json to the search URL to get data without an API key
        url = f"https://www.reddit.com/r/{sub}/search.json?q={query}&restrict_sr=1&sort=new&limit=15"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for post in data["data"]["children"]:
                    title = post["data"]["title"]
                    # Keyword safety check
                    if any(k in title.lower() for k in ["sunscreen", "spf", "sun screen"]):
                        link = "https://reddit.com" + post["data"]["permalink"]
                        posts.append((title[:120], link))
        except Exception as e:
            continue
            
    return posts

# -------------------------
# UI Styling
# -------------------------

st.markdown("""
<style>
.stApp { background-color: #E8B57A; }
h1, h2, h3 { color: #7A4E2D; }
.stButton > button { background-color: #D9D9D9; color: black; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🌻 AI Sunscreen Insight Engine")
st.caption("Accessing public Reddit discussions (No API Key Required).")

# -------------------------
# Search & Logic
# -------------------------

query = st.text_input("Search query", placeholder="Try: oily skin sunscreen")

if st.button("Fetch & Analyze"):
    if not query:
        st.warning("Please enter a query.")
    else:
        with st.spinner("Searching Reddit..."):
            posts = fetch_reddit_posts(query)

        if not posts:
            st.error("Reddit is currently limiting requests or no posts were found. Try again in a minute.")
        else:
            st.subheader("Top Discussions")
            for text, link in posts[:5]:
                st.markdown(f"- {text} \n[Link]({link})")

            # Simple Complaint Counter
            complaints = {
                "White Cast": ["white cast", "ashy", "grey"],
                "Greasy": ["greasy", "oily", "sticky"],
                "Acne": ["acne", "pimple", "breakout"]
            }
            
            counts = {k: 0 for k in complaints}
            for title, _ in posts:
                for cat, keywords in complaints.items():
                    if any(kw in title.lower() for kw in keywords):
                        counts[cat] += 1
            
            df = pd.DataFrame({"Category": list(counts.keys()), "Count": list(counts.values())})
            
            st.subheader("Complaint Analysis")
            chart = alt.Chart(df).mark_bar(color="#C27A2C").encode(
                x="Category", y="Count"
            ).properties(width=600, height=300)
            st.altair_chart(chart)
