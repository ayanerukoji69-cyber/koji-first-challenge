import os
import feedparser
import google.generativeai as genai

# 1. Geminiの設定（GitHub Secretsから鍵を読み込む）
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

# 2. 巡回ルート
RSS_URLS = [
    "https://news.yahoo.co.jp/rss/topics/top-picks.xml",
    "https://news.yahoo.co.jp/rss/categories/business.xml",
    "https://news.yahoo.co.jp/rss/categories/world.xml",
    "https://prtimes.jp/main/php/index.php?obj=rss&method=index"
]

# 3. キーワード
KEYWORDS = ["発表", "提携", "買収", "出資", "開業", "参入", "決算", "実証実験", "制裁", "関税", "輸出規制", "利下げ"]

def fetch_news():
    matched = []
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            found_kws = [kw for kw in KEYWORDS if kw in entry.title]
            if found_kws:
                matched.append({"title": entry.title, "link": entry.link})
    return {v['link']: v for v in matched}.values()

def summarize_news(articles):
    if not articles:
        return "本日の該当ニュースはありませんでした。"
    
    text_to_summarize = "\n".join([f"タイトル: {a['title']}" for a in articles])
    
    prompt = f"""
    以下のニュースタイトルリストを読み取り、ビジネスに関心がある人向けに
    「日経新聞の要約」のようなトーンで、重要なものを5件程度ピックアップして
    それぞれ1行〜2行で要約してください。
    
    {text_to_summarize}
    """
    
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    print("--- ニュース収集開始 ---")
    news_list = fetch_news()
    print(f"{len(news_list)}件の記事を抽出しました。AIで要約中...")
    
    summary = summarize_news(news_list)
    print("\n=== AI要約結果 ===\n")
    print(summary)
