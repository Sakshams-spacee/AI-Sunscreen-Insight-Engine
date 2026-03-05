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
