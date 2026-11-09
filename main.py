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
        json.dump(sent_list[-100:], f)

# مصادر RSS قوية ومحدثة لكرة القدم
FOOTBALL_RSS_FEEDS = [
    "https://www.transfermarkt.co.uk/rss/news",
    "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.skysports.com/rss/12040",
    "https://talksport.com/rss/football/feed",
    "https://www.espn.com/espn/rss/soccer/news",
    "https://90min.com/posts.rss"
]

def translate_and_format(text):
    """دالة ترجمة فورية واحترافية للغة العربية الفصحى"""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q={requests.utils.quote(text)}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            translated = "".join([item[0] for item in result[0] if item[0]])
            return translated
    except Exception as e:
        print(f"Translation Error: {e}")
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
    print("Stable Arabic Football Bot started...")
    sent_news = load_sent_news()
    news_sent_count = 0
    
    for url in FOOTBALL_RSS_FEEDS:
        try:
            print(f"Checking RSS Feed: {url}")
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:5]:
                link = entry.link
                if link in sent_news:
                    continue
                
                raw_title = entry.title
                raw_summary = entry.get("summary", entry.get("description", ""))
                source_name = feed.feed.get("title", "مصدر رياضي عالمي")
                
                print(f"Found new article: {raw_title}")
                
                # دمج العنوان والملخص وترجمتهم باحترافية للعربية
                full_raw_text = f"{raw_title}. {raw_summary[:200]}"
                arabic_text = translate_and_format(full_raw_text)
                
                # صياغة الرسالة النهائية بأسلوب رياضي أنيق
                message = f"⚽ **{arabic_text}**\n\n📌 **المصدر:** {source_name}\n🔗 [اقرأ التفاصيل من هنا]({link})"
                
                send_telegram_message(message)
                
                sent_news.append(link)
                news_sent_count += 1
                break # نكتفي بخبر جديد ممتاز في كل دورة
                
            if news_sent_count > 0:
                break
        except Exception as e:
            print(f"Error parsing feed {url}: {e}")
            
    save_sent_news(sent_news)
    print("Task completed successfully. Exiting now.")

if __name__ == "__main__":
    main()
    sys.exit(0)
