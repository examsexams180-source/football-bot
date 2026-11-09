import os
import requests
import feedparser
import sys

# بيانات التيليجرام والبوت ومفتاح Grok الخاصة بك
TELEGRAM_BOT_TOKEN = "9113301542:AAGAltyA38C8YTJWeFPf1PtnuVY40PaC0cE"
TELEGRAM_CHAT_ID = "-1003976750898"
GROK_API_KEY = "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"

# مصادر RSS مخصصة لكرة القدم والرياضة فقط
FOOTBALL_RSS_FEEDS = [
    "https://www.transfermarkt.co.uk/rss/news",
    "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.skysports.com/rss/12040",
    "https://talksport.com/rss/football/feed"
]

def summarize_with_grok(news_title):
    """دالة لترجمة وتلخيص وإعادة صياغة الخبر باستخدام ذكاء Grok الاصطناعي باللغة العربية"""
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"قم بترجمة هذا الخبر الرياضي إلى اللغة العربية، ولخصه وأعد صياغته بأسلوب احترافي وجذاب ومثير للاهتمام لعشاق كرة القدم:\n\n{news_title}"
    
    payload = {
        "model": "grok-2",  # استخدام النموذج القياسي المستقر
        "messages": [
            {"role": "system", "content": "أنت محرر رياضي محترف ومتخصص في ترجمة وتلخيص أخبار كرة القدم باللغة العربية."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            return data["choices"]["message"]["content"].strip()
        else:
            print(f"Grok API failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Grok API Error: {e}")
    
    # في حال حدوث أي استثناء، نرجع العنوان الأصلي كخطة بديلة
    return news_title

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
    print("Smart Football Bot worker started...")
    
    # نأخذ أحدث خبر من أول مصدر رياضي نشط
    for url in FOOTBALL_RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                latest_entry = feed.entries[0]
                raw_title = latest_entry.title
                link = latest_entry.link
                source_name = feed.feed.get("title", "مصدر رياضي")
                
                print(f"Processing news from: {source_name}")
                
                # ترجمة وتلخيص الخبر عبر ذكاء Grok بالعربية
                summarized_news = summarize_with_grok(raw_title)
                
                # صياغة الرسالة النهائية باللغة العربية
                message = f"⚽ **{summarized_news}**\n\n📌 **المصدر:** {source_name}\n🔗 [اقرأ التفاصيل من هنا]({link})"
                
                # إرسال الخبر للتيليجرام
                send_telegram_message(message)
                break  # نكتفي بخبر واحد ممتاز في كل دورة
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            
    print("Task completed successfully. Exiting now.")

if __name__ == "__main__":
    main()
    sys.exit(0)
