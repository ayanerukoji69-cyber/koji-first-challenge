import os
import json
import requests
import feedparser
import google.generativeai as genai

# 1. 各種設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

genai.configure(api_key=GEMINI_API_KEY)

# モデル名の指定を、より確実な方法に変更
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

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
    # リストを文字列に変換
    text = "\n".join(news_list)
    prompt = f"以下のニュースをビジネスマン向けに短く要約して:\n{text}"
    
    # 生成実行
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
    print(f"{len(articles)}件の記事が見つかりました。")
    
    try:
        summary = summarize_news(articles)
        if summary:
            send_line(summary)
            print("LINEに送信しました！")
        else:
            print("要約対象がありませんでした。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
