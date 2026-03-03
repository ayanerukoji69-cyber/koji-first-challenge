import feedparser

# 1. 巡回ルート（RSSフィード）の設定
RSS_URLS = [
    "https://news.yahoo.co.jp/rss/topics/top-picks.xml",    # Yahoo主要
    "https://news.yahoo.co.jp/rss/categories/business.xml",  # Yahoo経済
    "https://news.yahoo.co.jp/rss/categories/world.xml",     # Yahoo国際
    "https://prtimes.jp/main/php/index.php?obj=rss&method=index", # PR TIMES
    "https://jp.reuters.com/rss/topNews"                    # ロイター
]

# 2. キーワード
KEYWORDS = [
    "発表", "提携", "買収", "出資", "開業", "参入", "撤退", "決算", "実証実験", "キャンペーン",
    "制裁", "関税", "輸出規制", "停戦", "軍事", "軍事衝突", "首脳会談", "通商協議", "中央銀行", "利下げ", "原油"
]

def fetch_and_filter():
    print("--- ニュースの取得を開始します ---")
    matched_articles = []

    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # タイトルまたは本文にキーワードが含まれているかチェック
            title = entry.title
            summary = entry.get('summary', '')
            link = entry.link
            
            # キーワードマッチング
            found_kws = [kw for kw in KEYWORDS if kw in title or kw in summary]
            
            if found_kws:
                matched_articles.append({
                    "title": title,
                    "link": link,
                    "keywords": list(set(found_kws))
                })

    # 重複の削除（URLで判定）
    unique_articles = {v['link']: v for v in matched_articles}.values()
    
    return list(unique_articles)

# 実行テスト
if __name__ == "__main__":
    articles = fetch_and_filter()
    for i, art in enumerate(articles, 1):
        print(f"{i}. [{art['keywords']}] {art['title']}")
        print(f"   URL: {art['link']}\n")
