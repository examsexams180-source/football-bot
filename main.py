import os
import requests
import feedparser
import sys

# ضع بياناتك هنا مباشرة
TELEGRAM_BOT_TOKEN = "ضع_توكن_البوت_هنا"
TELEGRAM_CHAT_ID = "ضع_آيدي_الجروب_هنا"
RSS_FEED_URL = "ضع_رابط_الـ_RSS_هنا"

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
    message = f"⚽ **خبر رياضي جديد**\n\n{title}\n\n🔗 [اقرأ التفاصيل]({link})"
    
    # إرسال الخبر
    send_telegram_message(message)
    print("Task completed successfully. Exiting now.")

if __name__ == "__main__":
    main()
    # إنهاء السكريبت تماماً لكي لا يبقى معلقاً في GitHub Actions
    sys.exit(0)
