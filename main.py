import os
import feedparser
import google.generativeai as genai

# 1. Geminiの設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 安定して動く最新のモデル指定方法
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. ニュース収集の設定
RSS_URLS = [
    "https://news.yahoo.co.jp/rss/topics/top-picks.xml",
    "https://news.yahoo.co.jp/rss/categories/business.xml",
    "https://prtimes.jp/main/php/index.php?obj=rss&method=index"
]

KEYWORDS = ["発表", "提携", "買収", "出資", "開業", "参入", "決算", "実証実験"]

def fetch_news():
    matched = []
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if any(kw in entry.title for kw in KEYWORDS):
                matched.append({"title": entry.title, "link": entry.link})
    # 重複削除
    return {v['link']: v for v in matched}.values()

def summarize_news(articles):
    if not articles:
        return "本日の該当ニュースはありませんでした。"
    
    text_to_summarize = "\n".join([f"・{a['title']}" for a in articles])
    
    prompt = f"""
    以下のニュースリストを、経済に詳しいプロの編集者のように要約してください。
    【重要度が高いもの】を中心に5件ほど選び、
    それぞれ「何が起きたのか」「なぜ重要なのか」を1〜2行で簡潔にまとめてください。
    
    {text_to_summarize}
    """
    
    # ここでAIを呼び出し
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    print("--- ニュース収集開始 ---")
    news_list = list(fetch_news())
    print(f"{len(news_list)}件の記事を抽出しました。AIで要約中...")
    
    try:
        summary = summarize_news(news_list)
        print("\n=== AI要約結果 ===\n")
        print(summary)
    except Exception as e:
        print(f"AI要約中にエラーが発生しました: {e}")
