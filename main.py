import os
import requests
import feedparser
import sys

# بيانات التيليجرام الخاصة بك
TELEGRAM_BOT_TOKEN = "9113301542:AAGAltyA38C8YTJWeFPf1PtnuVY40PaC0cE"
TELEGRAM_CHAT_ID = "-1003976750898"

# مصادر RSS مخصصة لكرة القدم فقط
FOOTBALL_RSS_FEEDS = [
    "https://www.transfermarkt.co.uk/rss/news",
    "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.skysports.com/rss/12040",
    "https://talksport.com/rss/football/feed"
]

def translate_to_arabic(text):
    """دالة لترجمة النص تلقائياً إلى اللغة العربية عبر محرك ترجمة مجاني وسريع"""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q={requests.utils.quote(text)}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            translated_text = "".join([item[0] for item in result[0] if item[0]])
            return translated_text
    except Exception as e:
        print(f"Translation Error: {e}")
    return text

def send_telegram_message(message):
    """إرسال الرسالة إلى تيليجرام"""
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
    print("Smart Football Bot worker started...")
    
    for url in FOOTBALL_RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                latest_entry = feed.entries[0]
                raw_title = latest_entry.title
                link = latest_entry.link
                source_name = feed.feed.get("title", "Transfermarkt / مصدر رياضي")
                
                print(f"Processing news: {raw_title}")
                
                # ترجمة الخبر للغة العربية
                arabic_title = translate_to_arabic(raw_title)
                
                # صياغة الرسالة النهائية باللغة العربية
                message = f"⚽ **{arabic_title}**\n\n📌 **المصدر:** {source_name}\n🔗 [اقرأ التفاصيل من هنا]({link})"
                
                send_telegram_message(message)
                break
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            
    print("Task completed successfully. Exiting now.")

if __name__ == "__main__":
    main()
    sys.exit(0)
