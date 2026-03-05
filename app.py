import streamlit as st
import requests
import pandas as pd
import altair as alt
import re

# -------------------------
# Reddit Fetch Function
# -------------------------

def fetch_reddit_posts(query):

    subreddits = [
        "IndianSkincareAddicts",
        "skincareaddictsindia",
        "IndianBeautyTalks",
        "SkinSolutionsindia"
    ]

    headers = {"User-Agent": "insight-engine"}
    posts = []

    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/search.json?q={query}&limit=10&restrict_sr=1"
        response = requests.get(url, headers=headers)
        data = response.json()

        for post in data["data"]["children"]:
            title = post["data"]["title"].lower()

            # keep only sunscreen related posts
            if "sunscreen" not in title and "spf" not in title and "sun screen" not in title:
                continue

            clean_text = title.replace("&#x200b;", "")
            link = "https://reddit.com" + post["data"]["permalink"]
            posts.append((clean_text, link))

    return posts


# -------------------------
# Extract Evidence Quotes
# -------------------------

def extract_evidence(posts, keywords):

    quotes = []

    for text, link in posts:
        for k in keywords:
            if k in text:
                quotes.append((text[:120], link))
                break

        if len(quotes) >= 2:
            break

    return quotes


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
# App Title
# -------------------------

st.title("🌻 AI Sunscreen Consumer Insight Engine")
st.caption("Discover sunscreen product opportunities using real consumer discussions.")


# -------------------------
# Complaint Keywords
# -------------------------

complaint_keywords = {
    "white cast / dark skin": ["white cast","dark skin","melanin","ashy","grey cast"],
    "greasy texture": ["greasy","oily","sticky"],
    "melting in heat": ["melt","melting","sweat","humidity","hot"],
    "breakouts": ["acne","breakout","pimple","clog"],
    "reapplication": ["reapply","reapplication"]
}


# -------------------------
# Search Query
# -------------------------

query = st.text_input(
    "Search query",
    placeholder="Try your query"
)

query_lower = query.lower()


# -------------------------
# Button Action
# -------------------------

if st.button("Fetch, filter & generate product ideas"):

    posts = fetch_reddit_posts(query)

    # -------------------------
    # Reddit discussions
    # -------------------------

    st.subheader("Reddit Discussions")

    if len(posts) == 0:
        st.write("No sunscreen discussions found for this query.")

    for text, link in posts[:5]:
        st.markdown(f"- {text[:120]}  \n[View discussion]({link})")

    # -------------------------
    # Complaint Detection
    # -------------------------

    counts = {key: 0 for key in complaint_keywords}

    for text, link in posts:
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
            x=alt.X(
                "Complaint:N",
                axis=alt.Axis(labelAngle=0, labelColor="#7A4E2D", titleColor="#7A4E2D")
            ),
            y=alt.Y(
                "Frequency:Q",
                axis=alt.Axis(labelColor="#7A4E2D", titleColor="#7A4E2D")
            )
        ).properties(
            width=650,
            height=350,
            background="#F6D59C"
        )

        st.altair_chart(chart, use_container_width=True)

    else:
        st.write("No clear sunscreen complaints detected.")

    # -------------------------
    # Product Opportunities
    # -------------------------

    st.subheader("💡 Product Opportunities")

    ideas = []

    # query-driven ideas
    if "dark" in query_lower or "melanin" in query_lower:
        ideas.append(("Invisible sunscreen for melanin-rich Indian skin tones",
                      ["white cast","dark skin","melanin"]))

    if "oily" in query_lower:
        ideas.append(("Oil-control sunscreen gel for oily skin",
                      ["oily","greasy"]))

    if "acne" in query_lower:
        ideas.append(("Non-comedogenic sunscreen for acne-prone skin",
                      ["acne","pimple"]))

    if "sport" in query_lower or "sweat" in query_lower:
        ideas.append(("Sweat-resistant sport sunscreen for outdoor use",
                      ["sweat","humidity"]))

    # complaint-driven ideas
    if counts["white cast / dark skin"] > 0:
        ideas.append(("Tinted sunscreen eliminating white cast",
                      complaint_keywords["white cast / dark skin"]))

    if counts["greasy texture"] > 0:
        ideas.append(("Ultra-light matte sunscreen for humid climates",
                      complaint_keywords["greasy texture"]))

    if counts["melting in heat"] > 0:
        ideas.append(("Heat-stable sunscreen for extreme Indian summers",
                      complaint_keywords["melting in heat"]))

    if counts["breakouts"] > 0:
        ideas.append(("Dermatologist-tested acne-safe sunscreen",
                      complaint_keywords["breakouts"]))

    if counts["reapplication"] > 0:
        ideas.append(("Portable sunscreen stick for quick reapplication",
                      complaint_keywords["reapplication"]))

    # limit to 10 ideas
    ideas = ideas[:10]

    if len(ideas) == 0:
        ideas.append(("Lightweight sunscreen optimized for Indian climate", ["sunscreen"]))

    # display ideas
    for idea, keywords in ideas:

        st.markdown(f"**Idea:** {idea}")

        quotes = extract_evidence(posts, keywords)

        if len(quotes) > 0:
            st.write("Evidence from Reddit:")
            for q, link in quotes:
                st.markdown(f"• \"{q}\"  \n[Source]({link})")
        else:
            st.caption("Evidence: related discussions detected but no direct quote extracted.")