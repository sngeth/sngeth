"""Fetch latest blog posts from Atom feed and update README.md."""

import re
import urllib.request
import xml.etree.ElementTree as ET

FEED_URL = "https://sngeth.github.io/atom.xml"
README_PATH = "README.md"
MAX_POSTS = 5
ATOM_NS = "http://www.w3.org/2005/Atom"

START_MARKER = "<!-- BLOG-POSTS:START -->"
END_MARKER = "<!-- BLOG-POSTS:END -->"


def fetch_posts():
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "readme-updater"})
    with urllib.request.urlopen(req) as resp:
        tree = ET.parse(resp)
    entries = tree.findall(f"{{{ATOM_NS}}}entry")
    posts = []
    for entry in entries[:MAX_POSTS]:
        title = entry.findtext(f"{{{ATOM_NS}}}title")
        link = entry.find(f"{{{ATOM_NS}}}link").get("href")
        date_raw = entry.findtext(f"{{{ATOM_NS}}}updated", "")
        date = date_raw[:10] if date_raw else ""
        posts.append((title, link, date))
    return posts


def build_markdown(posts):
    lines = [START_MARKER]
    for title, link, date in posts:
        lines.append(f"- [{title}]({link}) — *{date}*")
    lines.append(END_MARKER)
    return "\n".join(lines)


def update_readme(posts_md):
    with open(README_PATH) as f:
        content = f.read()
    pattern = re.compile(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        re.DOTALL,
    )
    if pattern.search(content):
        new_content = pattern.sub(posts_md, content)
    else:
        new_content = content + "\n" + posts_md + "\n"
    with open(README_PATH, "w") as f:
        f.write(new_content)


if __name__ == "__main__":
    posts = fetch_posts()
    posts_md = build_markdown(posts)
    update_readme(posts_md)
    print(f"Updated README with {len(posts)} posts")
