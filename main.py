import os
import requests
import feedparser
import sys
import json

# بيانات التيليجرام والبوت ومفتاح Grok الخاص بك
TELEGRAM_BOT_TOKEN = "9113301542:AAGAltyA38C8YTJWeFPf1PtnuVY40PaC0cE"
TELEGRAM_CHAT_ID = "-1003976750898"
GROK_API_KEY = "grok_597c29bf36d4744f2978f187039eac33_308f81e4e270c35caf567b540c75aed24d8f82ae45fbeac50638882a87791e0c"

# ملف حفظ الأخبار المرسلة لمنع التكرار
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

# قائمة واسعة ومحدثة لمصادر كرة القدم والرياضة العالمية (RSS Feeds)
FOOTBALL_RSS_FEEDS = [
    "https://www.transfermarkt.co.uk/rss/news",
    "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.skysports.com/rss/12040",
    "https://talksport.com/rss/football/feed",
    "https://www.espn.com/espn/rss/soccer/news",
    "https://theathletic.com/feed/",
    "https://www.goal.com/feeds/en/news",
    "https://90min.com/posts.rss"
]

def test_and_summarize_with_grok(news_title, news_summary):
    """دالة اختبار وتلخيص عبر Grok مع طباعة التفاصيل بالكامل في الـ Logs"""
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    full_text = f"العنوان: {news_title}\nالمحتوى: {news_summary}"
    prompt = f"قم بقراءة هذا الخبر الرياضي، ولخصه وأعد صياغته بأسلوب احترافي وجذاب لعشاق كرة القدم باللغة العربية الفصحى (في حدود 3 أسطر):\n\n{full_text}"
    
    payload = {
        "model": "grok-2",
        "messages": [
            {"role": "system", "content": "أنت محرر رياضي محترف. قم بالتلخيص والترجمة بالعربية حصرياً."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    try:
        print("Sending request to Grok API...")
        response = requests.post(url, json=payload, headers=headers, timeout=25)
        print(f"Grok API Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            summary = data["choices"][0]["message"]["content"].strip()
            print("Grok Success! Summary generated.")
            return summary
        else:
            print(f"Grok API Failed Response: {response.text}")
    except Exception as e:
        print(f"Grok Exception Error: {e}")
        
    # في حال فشل الـ API، نرجع العنوان الأصلي كإحتياط
    return news_title

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
    print("Multi-source Anti-Duplicate Grok Bot started...")
    sent_news = load_sent_news()
    news_sent_count = 0
    
    for url in FOOTBALL_RSS_FEEDS:
        try:
            print(f"Checking RSS Feed: {url}")
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:3]:
                link = entry.link
                if link in sent_news:
                    continue
                
                raw_title = entry.title
                raw_summary = entry.get("summary", entry.get("description", ""))
                source_name = feed.feed.get("title", "مصدر رياضي عالمي")
                
                print(f"New unprocessed article found: {raw_title}")
                
                # تجربة تلخيص Grok مع طباعة حالته في الـ Logs
                grok_summary = test_and_summarize_with_grok(raw_title, raw_summary)
                
                message = f"⚽ **{grok_summary}**\n\n📌 **المصدر:** {source_name}\n🔗 [اقرأ التفاصيل من هنا]({link})"
                
                send_telegram_message(message)
                
                sent_news.append(link)
                news_sent_count += 1
                break # نكتفي بخبر جديد في كل دورة
                
            if news_sent_count > 0:
                break
        except Exception as e:
            print(f"Error parsing feed {url}: {e}")
            
    save_sent_news(sent_news)
    print("Task completed successfully. Exiting now.")

if __name__ == "__main__":
    main()
    sys.exit(0)
