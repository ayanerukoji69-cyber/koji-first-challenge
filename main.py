import os
import json
import requests
import feedparser
import google.generativeai as genai

# 1. 各種設定（GitHub Secretsから読み込み）
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. ニュース収集
RSS_URLS = [
    "https://news.yahoo.co.jp/rss/topics/top-picks.xml",
    "https://news.yahoo.co.jp/rss/categories/business.xml"
]
KEYWORDS = ["発表", "提携", "買収", "出資", "参入", "決算"]

def fetch_news():
    matched = []
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if any(kw in entry.title for kw in KEYWORDS):
                matched.append(entry.title)
    return list(set(matched))

def summarize_news(news_list):
    if not news_list: return None
    prompt = "以下のニュースリストから重要なものを数件選び、経済の専門家として200文字程度で要約して:\n" + "\n".join(news_list)
    response = model.generate_content(prompt)
    return response.text

def send_line(message):
    if not message: return
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    data = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": f"【AIニュース要約】\n{message}"}]
    }
    res = requests.post(url, headers=headers, data=json.dumps(data))
    print(f"LINE送信ステータス: {res.status_code}")

if __name__ == "__main__":
    print("ニュース確認中...")
    articles = fetch_news()
    summary = summarize_news(articles)
    
    if summary:
        send_line(summary)
        print("LINEに送信しました！")
    else:
        print("本日は該当するニュースがありませんでした。")
