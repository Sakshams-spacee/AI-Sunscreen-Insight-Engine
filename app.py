import streamlit as st
import pandas as pd
import altair as alt
import requests
import json

# -------------------------
# Serper.dev Search Function (The 2026 Stable Way)
# -------------------------

def fetch_reddit_insights(user_query):
    url = "https://google.serper.dev/search"
    
    # We target Indian subreddits specifically
    full_query = f'site:reddit.com (inurl:IndianSkincareAddicts OR inurl:skincareaddictsindia) "sunscreen" {user_query}'
    
    payload = json.dumps({"q": full_query})
    headers = {
        'X-API-KEY': st.secrets["serper_api_key"],
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        results = response.json()
        
        posts = []
        if "organic" in results:
            for item in results["organic"]:
                posts.append((item["title"], item["link"]))
        return posts
    except Exception as e:
        st.error(f"API Error: {e}")
        return []

# -------------------------
# UI Styling
# -------------------------

st.set_page_config(page_title="Sunscreen Insight Engine", page_icon="🌻")

st.markdown("""
<style>
.stApp { background-color: #E8B57A; }
h1, h2, h3 { color: #7A4E2D; }
.stButton > button { background-color: #D9D9D9; color: black; border-radius: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🌻 AI Sunscreen Insight Engine")
st.caption("Using Serper API for reliable, unblocked consumer data.")

# -------------------------
# User Input & Analysis
# -------------------------

query = st.text_input("Search query", placeholder="Try: oily skin white cast")

if st.button("Fetch & Analyze Insights"):
    if not query:
        st.warning("Please enter a search term.")
    else:
        with st.spinner("Accessing Reddit via Serper..."):
            posts = fetch_reddit_insights(query)

        if not posts:
            st.error("No results found. Please check if your API key is correctly added to Streamlit Secrets.")
        else:
            st.subheader("Top Reddit Threads")
            for title, link in posts[:5]:
                st.markdown(f"- **{title}** \n[Read Thread]({link})")

            # Simple Analytics
            complaint_map = {
                "White Cast": ["white cast", "ashy", "grey", "ghost"],
                "Greasy": ["greasy", "oily", "sticky", "heavy"],
                "Breakouts": ["acne", "pimple", "clog", "breakout"]
            }

            counts = {k: 0 for k in complaint_map}
            for title, _ in posts:
                t_low = title.lower()
                for cat, keywords in complaint_map.items():
                    if any(k in t_low for k in keywords):
                        counts[cat] += 1

            df = pd.DataFrame({"Issue": list(counts.keys()), "Count": list(counts.values())})

            st.subheader("Consumer Sentiment Analysis")
            if df["Count"].sum() > 0:
                chart = alt.Chart(df).mark_bar(color="#C27A2C").encode(
                    x=alt.X("Issue", sort="-y"),
                    y="Count"
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No specific complaints detected in the titles.")
