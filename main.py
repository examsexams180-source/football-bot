import os
import requests
import feedparser
import sys

# بيانات التيليجرام والبوت ومفتاح Grok الخاص بك
TELEGRAM_BOT_TOKEN = "9113301542:AAGAltyA38C8YTJWeFPf1PtnuVY40PaC0cE"
TELEGRAM_CHAT_ID = "-1003976750898"
GROK_API_KEY = "grok_597c29bf36d4744f2978f187039eac33_308f81e4e270c35caf567b540c75aed24d8f82ae45fbeac50638882a87791e0c"

# مصادر RSS مخصصة لكرة القدم فقط
FOOTBALL_RSS_FEEDS = [
    "https://www.transfermarkt.co.uk/rss/news",
    "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.skysports.com/rss/12040",
    "https://talksport.com/rss/football/feed"
]

def summarize_full_news_with_grok(news_title, news_summary):
    """دالة لإرسال عنوان وتفاصيل الخبر بالكامل إلى Grok لتلخيصه وصياغته بشكل احترافي بالعربية"""
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    full_text = f"العنوان: {news_title}\nالمحتوى: {news_summary}"
    prompt = f"قم بقراءة هذا الخبر الرياضي بالكامل، ولخصه وأعد صياغته بأسلوب احترافي وجذاب ومثير للاهتمام لعشاق كرة القدم باللغة العربية الفصحى (في حدود 3 إلى 4 أسطر):\n\n{full_text}"
    
    payload = {
        "model": "grok-2",
        "messages": [
            {"role": "system", "content": "أنت محرر رياضي محترف. مهمتك تلخيص أخبار كرة القدم بأسلوب شيق وجذاب باللغة العربية حصرياً."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        else:
            print(f"Grok API Error Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Grok Exception: {e}")
        
    return news_title

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
    print("Smart Grok Football Bot worker started...")
    
    for url in FOOTBALL_RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                latest_entry = feed.entries[0]
                raw_title = latest_entry.title
                raw_summary = latest_entry.get("summary", latest_entry.get("description", ""))
                link = latest_entry.link
                source_name = feed.feed.get("title", "مصدر رياضي")
                
                print(f"Processing full news from: {source_name}")
                
                grok_summary = summarize_full_news_with_grok(raw_title, raw_summary)
                
                message = f"⚽ **{grok_summary}**\n\n📌 **المصدر:** {source_name}\n🔗 [اقرأ التفاصيل من هنا]({link})"
                
                send_telegram_message(message)
                break
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            
    print("Task completed successfully. Exiting now.")

if __name__ == "__main__":
    main()
    sys.exit(0)
