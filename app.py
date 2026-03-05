import streamlit as st
import pandas as pd
import altair as alt
import requests
import json

# -------------------------
# Serper.dev Search Function
# -------------------------

def fetch_reddit_insights(user_query):
    url = "https://google.serper.dev/search"
    
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
st.caption("Discover sunscreen product opportunities using real consumer discussions.")

# -------------------------
# User Input
# -------------------------

query = st.text_input("Search query", placeholder="Try your query")

if st.button("Fetch & Analyze Insights"):

    if not query:
        st.warning("Please enter a search term.")

    else:

        with st.spinner("Accessing Reddit via Serper..."):
            posts = fetch_reddit_insights(query)

        if not posts:
            st.error("No results found. Please check if your API key is correctly added to Streamlit Secrets.")

        else:

            # -------------------------
            # Reddit Threads
            # -------------------------

            st.subheader("Top Reddit Threads")

            for title, link in posts[:5]:
                st.markdown(f"- **{title}**  \n[Read Thread]({link})")

            # -------------------------
            # Complaint Detection
            # -------------------------

            complaint_map = {
                "White Cast": ["white cast", "ashy", "grey", "ghost"],
                "Greasy": ["greasy", "oily", "sticky", "heavy"],
                "Breakouts": ["acne", "pimple", "clog", "breakout"],
                "Sweat / Heat Issues": ["sweat", "humidity", "melt", "hot"],
                "Reapplication Difficulty": ["reapply", "reapplication"]
            }

            counts = {k: 0 for k in complaint_map}

            for title, _ in posts:
                t_low = title.lower()

                for cat, keywords in complaint_map.items():
                    if any(k in t_low for k in keywords):
                        counts[cat] += 1

            df = pd.DataFrame({
                "Issue": list(counts.keys()),
                "Count": list(counts.values())
            })

            # -------------------------
            # Top Consumer Complaints
            # -------------------------

            st.subheader("Top Consumer Complaints")

            if df["Count"].sum() > 0:

                chart = alt.Chart(df).mark_bar(color="#C27A2C").encode(
    x=alt.X("Issue:N", sort="-y"),
    y=alt.Y("Count:Q", scale=alt.Scale(domain=[0, df["Count"].max()+1]))
).properties(height=300).properties(height=300)

                st.altair_chart(chart, use_container_width=True)

            else:
                st.info("No specific complaints detected in the titles.")

            # -------------------------
            # Product Innovation Engine
            # -------------------------

            st.subheader("💡 Product Innovation Opportunities")

            ideas = []
            evidence = []

            if counts["White Cast"] > 0:
                ideas.append("Invisible sunscreen formulated for melanin-rich Indian skin tones")
                evidence.append("Reddit users mention white cast or ashy sunscreen finish.")

            if counts["Greasy"] > 0:
                ideas.append("Ultra-matte gel sunscreen designed for humid Indian climates")
                evidence.append("Consumers complain about greasy sunscreen texture.")

            if counts["Breakouts"] > 0:
                ideas.append("Acne-safe sunscreen formulated for oily and acne-prone skin")
                evidence.append("Users report breakouts after sunscreen use.")

            if counts["Sweat / Heat Issues"] > 0:
                ideas.append("Sweat-resistant outdoor sunscreen for extreme Indian summers")
                evidence.append("Discussions mention sunscreen melting or sweating off.")

            if counts["Reapplication Difficulty"] > 0:
                ideas.append("Portable sunscreen stick or mist for easy reapplication")
                evidence.append("Consumers mention difficulty reapplying sunscreen.")

            if len(ideas) == 0:
                ideas.append("Lightweight daily sunscreen optimized for Indian summer conditions")
                evidence.append("General dissatisfaction with sunscreen performance.")

            for i in range(len(ideas)):

                st.markdown(f"**Idea:** {ideas[i]}")
                st.caption(f"Evidence: {evidence[i]}")

                if posts:
                    st.markdown(f"[Example Reddit Discussion]({posts[0][1]})")



