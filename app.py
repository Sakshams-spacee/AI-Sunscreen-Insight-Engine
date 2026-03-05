import streamlit as st
import requests
import pandas as pd
import altair as alt

# -------------------------
# Reddit Fetch Function
# -------------------------

def fetch_reddit_posts(query):

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    posts = []

    url = f"https://www.reddit.com/search.json?q={query}%20sunscreen&limit=25&sort=relevance"

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return []

        data = response.json()

        for post in data["data"]["children"]:

            title = post["data"]["title"].lower()

            if not any(word in title for word in ["sunscreen", "spf"]):
                continue

            clean_text = title.replace("&#x200b;", "")
            link = "https://reddit.com" + post["data"]["permalink"]

            posts.append((clean_text[:120], link))

    except Exception:
        return []

    return posts


# -------------------------
# UI Styling
# -------------------------

st.markdown("""
<style>
.stApp {
    background-color: #E8B57A;
}

h1, h2, h3 {
    color: #7A4E2D;
}

.stButton > button {
    background-color: #D9D9D9;
    color: black;
    border-radius: 10px;
}

div[data-baseweb="input"] input {
    background-color: #F0F0F0;
    color: black;
}

div[data-baseweb="input"] input::placeholder {
    color: #666666;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Title
# -------------------------

st.title("🌻 AI Sunscreen Consumer Insight Engine")
st.caption("Discover sunscreen product opportunities using real consumer discussions.")

# -------------------------
# Complaint Keywords
# -------------------------

complaint_keywords = {
    "white cast": ["white cast","ashy","grey"],
    "greasy texture": ["greasy","oily","sticky"],
    "melting in heat": ["melt","melting","sweat","humidity","hot"],
    "breakouts": ["acne","breakout","pimple"],
    "reapplication difficulty": ["reapply","reapplication"]
}

# -------------------------
# Search
# -------------------------

query = st.text_input(
    "Search query",
    placeholder="Try: dark skin, oily skin, humidity"
)

# -------------------------
# Button
# -------------------------

if st.button("Fetch, filter & generate product ideas"):

    posts = fetch_reddit_posts(query if query else "sunscreen")

    st.subheader("Reddit Discussions")

    if len(posts) == 0:
        st.write("No discussions found. Try another query.")
    else:
        for text, link in posts[:5]:
            st.markdown(f"- {text}  \n[View discussion]({link})")

    # -------------------------
    # Complaint Detection
    # -------------------------

    counts = {key: 0 for key in complaint_keywords}

    for post in posts:

        text = post[0].lower()

        for complaint, keywords in complaint_keywords.items():
            for word in keywords:
                if word in text:
                    counts[complaint] += 1

    df = pd.DataFrame({
        "Complaint": list(counts.keys()),
        "Frequency": list(counts.values())
    })

    df = df[df["Frequency"] > 0]

    st.subheader("Top Consumer Complaints")

    if len(df) > 0:

        chart = alt.Chart(df).mark_bar(
            size=25,
            color="#C27A2C"
        ).encode(
            x=alt.X("Complaint:N", axis=alt.Axis(labelAngle=0)),
            y="Frequency:Q"
        ).properties(
            width=650,
            height=350,
            background="#F6D59C"
        )

        st.altair_chart(chart, use_container_width=True)

    else:
        st.write("No clear sunscreen complaints detected.")

    # -------------------------
    # Product Ideas
    # -------------------------

    ideas = []
    evidence = []

    if counts["white cast"] > 0:
        ideas.append("Invisible sunscreen formulated for melanin-rich Indian skin tones")
        evidence.append("Consumers mention white cast or ashy finish.")

    if counts["greasy texture"] > 0:
        ideas.append("Ultra-matte gel sunscreen designed for humid Indian climates")
        evidence.append("Users report greasy sunscreen performance in humidity.")

    if counts["melting in heat"] > 0:
        ideas.append("Heat-resistant outdoor sunscreen for extreme Indian summers")
        evidence.append("Posts mention sunscreen melting or sweating off.")

    if counts["breakouts"] > 0:
        ideas.append("Acne-safe sunscreen formulated for oily skin")
        evidence.append("Users report pimples after sunscreen use.")

    if counts["reapplication difficulty"] > 0:
        ideas.append("Portable sunscreen mist or stick for quick reapplication")
        evidence.append("Consumers mention difficulty reapplying sunscreen.")

    if len(ideas) == 0:
        ideas.append("Lightweight sunscreen optimized for Indian summer conditions")
        evidence.append("General sunscreen dissatisfaction appears in discussions.")

    st.subheader("💡 Product Opportunities")

    for i in range(len(ideas)):
        st.markdown(f"**Idea:** {ideas[i]}")
        st.caption(f"Evidence: {evidence[i]}")
