import os
import requests
import feedparser
import sys
import json

# بيانات التيليجرام الخاصة بك
TELEGRAM_BOT_TOKEN = "9113301542:AAGAltyA38C8YTJWeFPf1PtnuVY40PaC0cE"
TELEGRAM_CHAT_ID = "-1003976750898"

# ملف حفظ الروابط المرسلة لمنع تكرار الأخبار نهائياً
SENT_NEWS_FILE = "sent_news.json"

def load_sent_news():
    if os.path.exists(SENT_NEWS_FILE):
        try:
            with open(SENT_NEWS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_sent_news(sent_list):
    with open(SENT_NEWS_FILE, "w") as f:
        json.dump(sent_list[-300:], f)

# قائمة واسعة وموثوقة 100% لأشهر مصادر كرة القدم العالمية
FOOTBALL_RSS_FEEDS = [
    {"name": "BBC Sport Football", "url": "https://feeds.bbci.co.uk/sport/football/rss.xml"},
    {"name": "Sky Sports Football", "url": "https://www.skysports.com/rss/12040"},
    {"name": "Transfermarkt News", "url": "https://www.transfermarkt.co.uk/rss/news"},
    {"name": "Goal.com News", "url": "https://www.goal.com/feeds/en/news"},
    {"name": "ESPN Soccer", "url": "https://www.espn.com/espn/rss/soccer/news"},
    {"name": "TalkSport Football", "url": "https://talksport.com/rss/football/feed"},
    {"name": "90min Football", "url": "https://90min.com/posts.rss"},
    {"name": "Football Italia", "url": "https://football-italia.net/feed/"},
    {"name": "Marca English", "url": "https://e00-marca.uecdn.es/rss/en/football.xml"},
    {"name": "AS English", "url": "https://en.as.com/rss/futbol/primera.xml"}
]

def translate_text(text):
    """ترجمة فورية واحترافية للغة العربية الفصحى"""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q={requests.utils.quote(text)}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return "".join([item[0] for item in result[0] if item[0]])
    except:
        pass
    return text

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Message sent successfully to Telegram!")
        else:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    print("Multi-source Football News Aggregator started...")
    sent_news = load_sent_news()
    articles_sent_count = 0
    
    # نمر على المصادر تباعاً لجلب أخبار متجددة
    for feed_info in FOOTBALL_RSS_FEEDS:
        if articles_sent_count >= 2: # نرسل خبرين في كل دورة تشغيل لضمان تدفق الأخبار
            break
            
        source_name = feed_info["name"]
        feed_url = feed_info["url"]
        
        try:
            print(f"Checking source: {source_name}")
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:5]:
                link = entry.link
                if link in sent_news:
                    continue
                
                raw_title = entry.title
                raw_summary = entry.get("summary", entry.get("description", ""))
                
                print(f"Found new article: {raw_title}")
                full_text = f"{raw_title}. {raw_summary}"
                arabic_text = translate_text(full_text)
                
                message = f"⚽ **{arabic_text}**\n\n📌 **المصدر:** {source_name}\n🔗 [اقرأ التفاصيل من هنا]({link})"
                
                send_telegram_message(message)
                
                sent_news.append(link)
                articles_sent_count += 1
                break
        except Exception as e:
            print(f"Error parsing {source_name}: {e}")
            
    save_sent_news(sent_news)
    print(f"Task completed. Total articles sent in this run: {articles_sent_count}")

if __name__ == "__main__":
    main()
    sys.exit(0)
