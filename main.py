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
    # ناحتفظ بآخر 200 رابط لمنع التكرار تماماً على مدار الأيام
    with open(SENT_NEWS_FILE, "w") as f:
        json.dump(sent_list[-200:], f)

# شبكة مصادر عالمية ضخمة ومتنوعة لأخبار كرة القدم من كل مكان في العالم
FOOTBALL_RSS_FEEDS = [
    {"name": "BBC Sport Football", "url": "https://feeds.bbci.co.uk/sport/football/rss.xml"},
    {"name": "Sky Sports Football", "url": "https://www.skysports.com/rss/12040"},
    {"name": "Transfermarkt News", "url": "https://www.transfermarkt.co.uk/rss/news"},
    {"name": "Goal.com", "url": "https://www.goal.com/feeds/en/news"},
    {"name": "ESPN Soccer", "url": "https://www.espn.com/espn/rss/soccer/news"},
    {"name": "TalkSport Football", "url": "https://talksport.com/rss/football/feed"},
    {"name": "90min Football", "url": "https://90min.com/posts.rss"}
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
    print("Global Football News Aggregator started...")
    sent_news = load_sent_news()
    article_sent = False
    
    # نمر على المصادر المختلفة بالتدريج للبحث عن خبر جديد لم يُرسل من قبل
    for feed_info in FOOTBALL_RSS_FEEDS:
        if article_sent:
            break
            
        source_name = feed_info["name"]
        feed_url = feed_info["url"]
        
        try:
            print(f"Checking source: {source_name}")
            feed = feedparser.parse(feed_url)
            
            # فحص أول 5 أخبار في كل مصدر
            for entry in feed.entries[:5]:
                link = entry.link
                
                # إذا كان الخبر أُرسل من قبل، نتخطاه ونبحث عن غيره
                if link in sent_news:
                    continue
                
                raw_title = entry.title
                raw_summary = entry.get("summary", entry.get("description", ""))
                
                print(f"Found new article from {source_name}: {raw_title}")
                
                # دمج العنوان والملخص وترجمتهم باحترافية للعربية
                full_raw_text = f"{raw_title}. {raw_summary}"
                arabic_text = translate_and_format(full_raw_text)
                
                # صياغة الرسالة النهائية بشكل أنيق وجذاب
                message = f"⚽ **{arabic_text}**\n\n📌 **المصدر:** {source_name}\n🔗 [اقرأ التفاصيل من هنا]({link})"
                
                send_telegram_message(message)
                
                # تسجيل الرابط ضمن الأخبار المرسلة
                sent_news.append(link)
                article_sent = True
                break
                
        except Exception as e:
            print(f"Error parsing feed {source_name}: {e}")
            
    save_sent_news(sent_news)
    print("Task completed successfully. Exiting now.")

if __name__ == "__main__":
    main()
    sys.exit(0)
