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
        "IndianBeautyTalks",
        "SkinSolutionsindia"
    ]

    posts = []

    for sub in subreddits:

        url = f"https://www.reddit.com/r/{sub}/search.rss?q={query}"

        try:
            response = requests.get(url)

            if response.status_code != 200:
                continue

            items = response.text.split("<item>")

            for item in items[1:6]:

                title = item.split("<title>")[1].split("</title>")[0].lower()

                if "sunscreen" not in title and "spf" not in title:
                    continue

                link = item.split("<link>")[1].split("</link>")[0]

                posts.append((title[:120], link))

        except:
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

