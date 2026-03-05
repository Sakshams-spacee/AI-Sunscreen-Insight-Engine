import streamlit as st
import requests
import pandas as pd
import altair as alt

def fetch_reddit_posts():
    subreddits = [
        "IndianSkincareAddicts",
        "skincareaddictsindia",
        "IndianBeautyTalks",
        "SkinSolutionsindia"
    ]

    headers = {"User-Agent": "Mozilla/5.0"}
    posts = []

    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/hot.json?limit=20"

        try:
            r = requests.get(url, headers=headers, timeout=10)
            data = r.json()

            for post in data["data"]["children"]:
                title = post["data"]["title"].lower()

                if "sunscreen" in title or "spf" in title:
                    link = "https://reddit.com" + post["data"]["permalink"]
                    posts.append((title, link))
        except:
            pass

    return posts


st.title("🌻 AI Sunscreen Consumer Insight Engine")
st.caption("Discover sunscreen product opportunities using real consumer discussions.")

complaint_keywords = {
    "white cast": ["white cast","ashy","grey"],
    "greasy texture": ["greasy","oily","sticky"],
    "melting in heat": ["melt","melting","sweat","humidity","hot"],
    "breakouts": ["acne","breakout","pimple"],
    "reapplication difficulty": ["reapply","reapplication"]
}

query = st.text_input("Search query", placeholder="dark skin, oily skin, humidity")

if st.button("Fetch insights"):

    posts = fetch_reddit_posts()

    st.subheader("Reddit Discussions")

    if len(posts) == 0:
        st.write("No sunscreen posts detected.")
    else:
        for text, link in posts[:5]:
            st.markdown(f"- {text}  \n[View discussion]({link})")

    counts = {k:0 for k in complaint_keywords}

    for p in posts:
        text = p[0]

        for complaint,words in complaint_keywords.items():
            for w in words:
                if w in text:
                    counts[complaint]+=1

    df = pd.DataFrame({
        "Complaint":list(counts.keys()),
        "Frequency":list(counts.values())
    })

    df = df[df["Frequency"]>0]

    st.subheader("Top Consumer Complaints")

    if len(df)>0:

        chart = alt.Chart(df).mark_bar(color="#C27A2C").encode(
            x=alt.X("Complaint:N",axis=alt.Axis(labelAngle=0)),
            y="Frequency:Q"
        )

        st.altair_chart(chart,use_container_width=True)

    ideas=[]
    evidence=[]

    if counts["white cast"]>0:
        ideas.append("Invisible sunscreen for melanin rich skin")
        evidence.append("Users complain about white cast.")

    if counts["greasy texture"]>0:
        ideas.append("Ultra matte sunscreen for humid climates")
        evidence.append("Users mention greasy sunscreen.")

    if counts["melting in heat"]>0:
        ideas.append("Heat resistant outdoor sunscreen")
        evidence.append("Posts mention sunscreen melting.")

    if counts["breakouts"]>0:
        ideas.append("Acne safe sunscreen")
        evidence.append("Users report breakouts.")

    if counts["reapplication difficulty"]>0:
        ideas.append("Portable sunscreen stick")
        evidence.append("Users struggle to reapply.")

    if len(ideas)==0:
        ideas.append("Lightweight daily sunscreen for Indian summers")
        evidence.append("General sunscreen dissatisfaction.")

    st.subheader("💡 Product Opportunities")

    for i in range(len(ideas)):
        st.markdown(f"**Idea:** {ideas[i]}")
        st.caption(f"Evidence: {evidence[i]}")
