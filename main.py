import os
import requests
import feedparser
import sys
import json
from datetime import datetime

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
    # نحتفظ بآخر 400 رابط لضمان عدم التكرار نهائياً
    with open(SENT_NEWS_FILE, "w") as f:
        json.dump(sent_list[-400:], f)

# روابط Google News RSS الشاملة لكل أخبار كرة القدم المحلية والعالمية
GOOGLE_NEWS_FEEDS = [
    {
        "name": "أخبار كرة القدم العامة (Google News)", 
        "url": "https://news.google.com/rss/search?q=%D9%83%D8%B1%D8%A9+%D9%82%D8%AF%D9%85&hl=ar&gl=EG&ceid=EG:ar"
    },
    {
        "name": "موقع بطولات - Btolat", 
        "url": "https://news.google.com/rss/search?q=site:btolat.com&hl=ar&gl=EG&ceid=EG:ar"
    },
    {
        "name": "موقع يلا كورة - YallaKora", 
        "url": "https://news.google.com/rss/search?q=site:yallakora.com&hl=ar&gl=EG&ceid=EG:ar"
    },
    {
        "name": "موقع كووورة - Kooora", 
        "url": "https://news.google.com/rss/search?q=site:kooora.com&hl=ar&gl=EG&ceid=EG:ar"
    },
    {
        "name": "الدوري الإنجليزي ودوري الأبطال", 
        "url": "https://news.google.com/rss/search?q=%D8%A7%D9%84%D8%AF%D9%88%D8%B1%D9%8A+%D8%A7%D9%84%D8%A5%D9%86%D8%AC%D9%84%D9%8A%D8%B2%D9%8A+OR+%D8%AF%D9%88%D8%B1%D9%8A+%D8%A3%D8%A8%D8%B7%D8%A7%D9%84+%D8%A3%D9%88%D8%B1%D9%88%D8%A8%D8%A7&hl=ar&gl=EG&ceid=EG:ar"
    }
]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True  # إلغاء معاينة الصور والروابط تماماً لتظهر الرسالة نصية نظيفة
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
    print("Google News Football Bot started...")
    sent_news = load_sent_news()
    articles_sent_count = 0
    
    # المرور على المصادر لجلب أحدث الأخبار
    for feed_info in GOOGLE_NEWS_FEEDS:
        if articles_sent_count >= 2: # نرسل خبرين في كل دورة تشغيل لضمان استمرارية النشر
            break
            
        source_name = feed_info["name"]
        feed_url = feed_info["url"]
        
        try:
            print(f"Checking source: {source_name}")
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:8]:
                link = entry.link
                if link in sent_news:
                    continue
                
                raw_title = entry.get("title", "")
                raw_summary = entry.get("summary", entry.get("description", ""))
                
                print(f"Found new article: {raw_title}")
                
                # تنسيق الرسالة بشكل أنيق ونظيف بدون صور
                message = f"⚽ **{raw_title}**\n\n"
                
                if raw_summary and len(raw_summary) > 10:
                    # تنظيف الملخص من أي أكواد HTML عشوائية
                    clean_summary = raw_summary.split('<')[0] if '<' in raw_summary else raw_summary
                    if len(clean_summary) > 10:
                        message += f"📝 {clean_summary}\n\n"
                
                message += f"📌 **المصدر:** {source_name}\n🔗 [اقرأ التفاصيل من هنا]({link})"
                
                send_telegram_message(message)
                
                sent_news.append(link)
                articles_sent_count += 1
                break
        except Exception as e:
            print(f"Error parsing {source_name}: {e}")
            
    save_sent_news(sent_news)
    print(f"Task completed. Total articles sent: {articles_sent_count}")

if __name__ == "__main__":
    main()
    sys.exit(0)
