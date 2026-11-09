import os
import requests
import feedparser
import sys

# بيانات التيليجرام والبوت الخاصة بك
TELEGRAM_BOT_TOKEN = "9113301542:AAGAltyA38C8YTJWeFPf1PtnuVY40PaC0cE"
TELEGRAM_CHAT_ID = "-1003976750898"
GROK_API_KEY = "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"

# قائمة واسعة تضم أشهر مصادر الأخبار العالمية والرياضية والتقنية (RSS Feeds)
RSS_FEEDS = [
    # --- كرة القدم والرياضة ---
    "https://www.transfermarkt.co.uk/rss/news",
    "https://feeds.bbci.co.uk/sport/rss.xml",
    "https://www.skysports.com/rss/12040",
    "https://talksport.com/rss/sports-news/all/feed",
    "https://www.espn.com/espn/rss/news",
    "https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml",
    "https://theathletic.com/feed/",
    
    # --- الأخبار العالمية والسياسية الكبرى ---
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "http://rss.cnn.com/rss/edition_world.rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "https://www.cbsnews.com/latest/rss/main/",
    "https://feeds.npr.org/1001/rss.xml",
    "https://time.com/feed/",
    "https://globalnews.ca/world/feed/",
    
    # --- التكنولوجيا والعلوم ---
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/rss",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.cnet.com/rss/all/",
    "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"
]

def send_telegram_message(message):
    """دالة لإرسال الرسالة إلى تيليجرام"""
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
    print("Multi-source news bot worker started...")
    
    news_found = False
    
    # المرور على كل روابط الـ RSS في القائمة وجلب أحدث خبر من كل مصدر
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                latest_entry = feed.entries[0]
                title = latest_entry.title
                link = latest_entry.link
                
                # صياغة وإرسال الخبر
                message = f"🌍 **خبر عاجل / رياضي جديد**\n\n{title}\n\n🔗 [اقرأ التفاصيل]({link})"
                send_telegram_message(message)
                news_found = True
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            
    if not news_found:
        print("No news found in any RSS feed.")
    
    print("Task completed successfully. Exiting now.")

if __name__ == "__main__":
    main()
    sys.exit(0)
