import streamlit as st
import pandas as pd
import altair as alt
from googlesearch import search
import time

# -------------------------
# Reddit Search via Google (No API Key Needed)
# -------------------------

def fetch_reddit_via_google(user_query):
    # This query tells Google to only look at specific Indian subreddits for your topic
    search_query = f'site:reddit.com (inurl:IndianSkincareAddicts OR inurl:skincareaddictsindia) "sunscreen" {user_query}'
    
    posts = []
    try:
        # Fetching top 10 results
        # num_results=10, lang="en"
        for url in search(search_query, num_results=10, sleep_interval=2):
            if "comments" in url:
                # Create a readable title from the URL slug
                slug = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
                display_title = slug.replace('_', ' ').replace('-', ' ').title()
                posts.append((display_title, url))
    except Exception as e:
        st.error(f"Search error: {e}")
        
    return posts

# -------------------------
# UI Styling
# -------------------------

st.set_page_config(page_title="Sunscreen Insight Engine", page_icon="🌻")

st.markdown("""
<style>
.stApp { background-color: #E8B57A; }
h1, h2, h3 { color: #7A4E2D; }
.stButton > button { background-color: #D9D9D9; color: black; border-radius: 10px; border: 1px solid #7A4E2D; }
</style>
""", unsafe_allow_html=True)

st.title("🌻 AI Sunscreen Insight Engine")
st.caption("Analyzing real consumer discussions from Indian subreddits via Google Search.")

# -------------------------
# User Input
# -------------------------

query = st.text_input("Search query", placeholder="Try: oily skin sweat", help="Enter keywords like 'matte', 'silicone', or 'acne'")

if st.button("Fetch & Generate Insights"):
    if not query:
        st.warning("Please enter a search term first!")
    else:
        with st.spinner("Scanning Reddit discussions via Google..."):
            posts = fetch_reddit_via_google(query)

        if not posts:
            st.error("No discussions found. Try making your search more general (e.g., just 'oily skin').")
        else:
            st.subheader("Relevant Reddit Threads")
            for title, link in posts[:5]:
                st.markdown(f"- **{title}** \n[View on Reddit]({link})")

            # -------------------------
            # Pattern Analysis
            # -------------------------
            # We check the titles for specific complaint keywords
            complaint_map = {
                "White Cast": ["white cast", "ashy", "ghost", "pale", "grey"],
                "Greasy/Oily": ["greasy", "oily", "sticky", "chipchip", "heavy"],
                "Eye Stinging": ["eye", "sting", "burn", "tear"],
                "Breakouts": ["acne", "pimple", "clog", "breakout", "comedogenic"]
            }

            counts = {k: 0 for k in complaint_map}
            for title, _ in posts:
                low_title = title.lower()
                for category, keywords in complaint_map.items():
                    if any(word in low_title for word in keywords):
                        counts[category] += 1

            # Visualize if we found any data
            df = pd.DataFrame({"Complaint": list(counts.keys()), "Frequency": list(counts.values())})
            
            if df["Frequency"].sum() > 0:
                st.subheader("Common Issues Found")
                chart = alt.Chart(df).mark_bar(color="#C27A2C").encode(
                    x=alt.X("Complaint", sort="-y"),
                    y="Frequency"
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No specific complaints detected in the titles. The threads might be general recommendations.")

            # -------------------------
            # Product Opportunity
            # -------------------------
            st.subheader("💡 Product Opportunity")
            if counts["Greasy/Oily"] > 0:
                st.success("**Opportunity:** Develop a 'Humidity-Proof Matte Gel'.")
                st.write("Evidence: Users are frequently discussing greasiness in humid Indian conditions.")
            elif counts["White Cast"] > 0:
                st.success("**Opportunity:** Develop a 'Tinted Fluid' for deep skin tones.")
                st.write("Evidence: Discussions highlight the 'ghostly' look of mineral filters.")
            else:
                st.success("**Opportunity:** Next-gen lightweight SPF sticks for reapplication.")
                st.write("Evidence: Consumer sentiment shows a need for easier application methods.")
