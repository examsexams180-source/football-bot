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
    # نحتفظ بآخر 300 رابط لضمان عدم تكرار أي خبر إطلاقاً
    with open(SENT_NEWS_FILE, "w") as f:
        json.dump(sent_list[-300:], f)

# قائمة مصادر RSS حقيقية ومتجددة لحظة بلحظة (عربية وعالمية)
FOOTBALL_RSS_FEEDS = [
    {"name": "موقع بطولات - مصر والعالم", "url": "https://www.btolat.com/rss/newsfeed"},
    {"name": "BBC Sport Football", "url": "https://feeds.bbci.co.uk/sport/football/rss.xml"},
    {"name": "Sky Sports Football", "url": "https://www.skysports.com/rss/12040"},
    {"name": "Transfermarkt News", "url": "https://www.transfermarkt.co.uk/rss/news"},
    {"name": "Goal.com News", "url": "https://www.goal.com/feeds/en/news"},
    {"name": "TalkSport Football", "url": "https://talksport.com/rss/football/feed"},
    {"name": "90min Football", "url": "https://90min.com/posts.rss"}
]

def translate_text(text):
    """دالة ترجمة ذكية (لو النص عربي سيبقيه كما هو، ولو إنجليزي سيترجمه للعربية بامتياز)"""
    # لو النص عربي بالأساس لن نحتاج ترجمة جبارة، لكن للتأكيد نمرره على الترجمة
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ar&dt=t&q={requests.utils.quote(text)}"
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
    print("Super Football News Aggregator started...")
    sent_news = load_sent_news()
    articles_sent_count = 0
    
    # المرور على المصادر لجلب أخبار جديدة متجددة
    for feed_info in FOOTBALL_RSS_FEEDS:
        if articles_sent_count >= 2: # نرسل خبرين في كل دورة تشغيل لتحديث الجروب باستمرار
            break
            
        source_name = feed_info["name"]
        feed_url = feed_info["url"]
        
        try:
            print(f"Checking source: {source_name}")
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:8]: # فحص أول 8 أخبار في كل مصدر لضمان إيجاد الخبر الجديد فوراً
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
            print(f"Error parsing {source_name
