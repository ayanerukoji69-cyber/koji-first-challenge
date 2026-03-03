import os
import json
import requests
import feedparser
from google import genai

# 1. 各種設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

# APIの初期化
client = genai.Client(api_key=GEMINI_API_KEY)

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
    if not news_list:
        return None

    text = "\n".join(news_list)
    prompt = f"以下のニュースリストから重要なトピックを選び、150文字程度で要約して。箇条書きを使って:\n{text}"

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # ✅ 最新安定版に更新
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini生成エラー: {e}")
        return None

def send_line(message):
    if not message:
        return
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
    print(f"{len(articles)}件の記事が見つかりました。AIで要約を開始します。")

    summary = summarize_news(articles)

    if summary:
        send_line(summary)
        print("LINEに送信完了しました！")
    else:
        print("要約が生成されませんでした。")
