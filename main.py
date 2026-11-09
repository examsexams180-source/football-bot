import os
import requests
import feedparser
import sys

# بيانات التيليجرام والبوت الخاصة بك
TELEGRAM_BOT_TOKEN = "9113301542:AAGAltyA38C8YTJWeFPf1PtnuVY40PaC0cE"
TELEGRAM_CHAT_ID = "-1003976750898"
GROK_API_KEY = "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"

# رابط خلاصة الـ RSS لموقع Transfermarkt
RSS_FEED_URL = "https://www.transfermarkt.co.uk/rss/news"

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
    print("News bot worker started...")
    
    # جلب وقراءة محتوى الـ RSS
    feed = feedparser.parse(RSS_FEED_URL)
    
    if not feed.entries:
        print("No news found in the RSS feed.")
        sys.exit(0)
    
    # جلب أحدث خبر (أول خبر في القائمة)
    latest_entry = feed.entries[0]
    title = latest_entry.title
    link = latest_entry.link
    
    # صياغة الرسالة
    message = f"⚽ **خبر رياضي جديد من Transfermarkt**\n\n{title}\n\n🔗 [اقرأ التفاصيل]({link})"
    
    # إرسال الخبر
    send_telegram_message(message)
    print("Task completed successfully. Exiting now.")

if __name__ == "__main__":
    main()
    # إنهاء السكريبت تماماً لكي لا يبقى معلقاً في GitHub Actions
    sys.exit(0)
