import streamlit as st
import pandas as pd
import altair as alt
import praw

# -------------------------
# Reddit Fetch Function (PRAW Version)
# -------------------------

def fetch_reddit_posts(query):
    # Retrieve credentials from Streamlit Secrets (for security)
    try:
        reddit = praw.Reddit(
            client_id=st.secrets["reddit_client_id"],
            client_secret=st.secrets["reddit_client_secret"],
            user_agent="SunscreenInsightEngine/1.0 (by /u/YOUR_REDDIT_USERNAME)"
        )

        subreddits = [
            "IndianSkincareAddicts",
            "skincareaddictsindia",
            "IndianBeautyTalks",
            "SkinSolutionsindia"
        ]

        posts = []
        
        # We combine the subreddits into one search for efficiency
        sub_list = "+".join(subreddits)
        search_results = reddit.subreddit(sub_list).search(query, limit=20)

        for submission in search_results:
            title = submission.title.lower()
            
            # Simple keyword filter to ensure relevance
            if any(k in title for k in ["sunscreen", "spf", "sun screen"]):
                clean_text = submission.title.replace("&#x200b;", "")
                link = "https://reddit.com" + submission.permalink
                posts.append((clean_text[:120], link))

        return posts
    except Exception as e:
        st.error(f"Error connecting to Reddit: {e}")
        return []

# -------------------------
# UI Styling
# -------------------------

st.markdown("""
<style>
.stApp { background-color: #E8B57A; }
h1, h2, h3 { color: #7A4E2D; }
.stButton > button { background-color: #D9D9D9; color: black; border-radius: 10px; }
div[data-baseweb="input"] input { background-color: #F0F0F0; color: black; }
</style>
""", unsafe_allow_html=True)

st.title("🌻 AI Sunscreen Consumer Insight Engine")
st.caption("Using official Reddit API for live consumer discussions.")

# -------------------------
# Complaint Keywords
# -------------------------

complaint_keywords = {
    "white cast / dark skin suitability": ["white cast","dark skin","melanin","ashy","grey cast"],
    "greasy/oily texture": ["greasy","oily","sticky"],
    "melting in heat": ["melt","melting","sweat","humidity","hot"],
    "breakouts/acne": ["acne","breakout","pimple","clog"],
    "reapplication difficulty": ["reapply","reapplication"]
}

query = st.text_input("Search query", placeholder="Try: sunscreen india heat sweat")

if st.button("Fetch, filter & generate product ideas"):
    
    if not query:
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Fetching data from Reddit..."):
            posts = fetch_reddit_posts(query)

        st.subheader("Reddit Discussions")

        if len(posts) == 0:
            st.write("No sunscreen discussions found. Check your API credentials or try a broader search.")
        else:
            for text, link in posts[:5]:
                st.markdown(f"- {text}  \n[View discussion]({link})")

            # -------------------------
            # Complaint Detection Logic
            # -------------------------
            counts = {key: 0 for key in complaint_keywords}
            for post in posts:
                text = post[0].lower()
                for complaint, keywords in complaint_keywords.items():
                    for word in keywords:
                        if word in text:
                            counts[complaint] += 1

            df = pd.DataFrame({"Complaint": list(counts.keys()), "Frequency": list(counts.values())})
            df = df[df["Frequency"] > 0]

            st.subheader("Top Consumer Complaints")
            if not df.empty:
                chart = alt.Chart(df).mark_bar(size=25, color="#C27A2C").encode(
                    x=alt.X("Complaint:N", axis=alt.Axis(labelAngle=0)),
                    y="Frequency:Q"
                ).properties(width=650, height=350, background="#F6D59C")
                st.altair_chart(chart, use_container_width=True)
            else:
                st.write("No specific complaints detected in these posts.")

            # -------------------------
            # Product Opportunities
            # -------------------------
            st.subheader("💡 Product Opportunities")
            ideas = []
            if counts["white cast / dark skin suitability"] > 0: ideas.append("Invisible sunscreen for melanin-rich skin")
            if counts["greasy/oily texture"] > 0: ideas.append("Ultra-matte gel for humid climates")
            if counts["melting in heat"] > 0: ideas.append("Heat-resistant sweat-proof formula")
            
            if not ideas:
                st.write("General lightweight sunscreen for Indian summer conditions.")
            else:
                for idea in ideas:
                    st.markdown(f"* **Idea:** {idea}")
