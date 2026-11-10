import os
import requests
import feedparser
import sys
import json
from bs4 import BeautifulSoup

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
        json.dump(sent_list[-400:], f)

# مصادر Google News RSS شاملة لكل أخبار الكرة
GOOGLE_NEWS_FEEDS = [
    {
        "name": "أخبار كرة القدم العامة", 
        "url": "https://news.google.com/rss/search?q=%D9%83%D8%B1%D8%A9+%D9%82%D8%AF%D9%85&hl=ar&gl=EG&ceid=EG:ar"
    },
    {
        "name": "موقع بطولات - Btolat", 
        "url": "https://news.google.com/rss/search?q=site:btolat.com&hl=ar&gl=EG&ceid=EG:ar"
    },
    {
        "name": "موقع يلا كورة - YallaKora", 
        "url": "https://news.google.com/rss/search?q=site:yallakora.com&hl=ar&gl=EG&ceid=EG:ar"
    }
]

def fetch_full_article_text(url):
    """دالة تقوم بالدخول على رابط الخبر وسحب تفاصيله الكاملة لكي يقرأها المتابع من التيليجرام مباشرة"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # محاولة استخراج الفقرات النصية من المقال
            paragraphs = soup.find_all('p')
            article_text = ""
            for p in paragraphs:
                text = p.get_text().strip()
                # نأخذ الفقرات المفيدة التي طولها أكبر من 30 حرفاً
                if len(text) > 30 and "حقوق الملكية" not in text and "جميع الحقوق محفوظة" not in text:
                    article_text += text + "\n\n"
                    if len(article_text) > 600:  # نكتفي بأول 600 حرف ليكون الخبر مكثفاً ومرتباً
                        break
            
            if len(article_text) > 50:
                return article_text.strip()
    except Exception as e:
        print(f"Error scraping article text: {e}")
    
    return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True  # إلغاء الصور والمعاينة نهائياً
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
    print("Full Content Football Bot started...")
    sent_news = load_sent_news()
    articles_sent_count = 0
    
    for feed_info in GOOGLE_NEWS_FEEDS:
        if articles_sent_count >= 2: # خبرين في كل دورة تشغيل
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
                print(f"Found article to process: {raw_title}")
                
                # جلب تفاصيل الخبر الكاملة من داخل الموقع
                full_details = fetch_full_article_text(link)
                
                # بناء رسالة متكاملة وغنية بالمعلومات
                message = f"⚽ **{raw_title}**\n\n"
                
                if full_details:
                    message += f"📄 {full_details}\n\n"
                else:
                    message += f"📌 تفاصيل عاجلة ومتابعة حصرية لقاء أحداث المباراة والفعاليات الرياضية لحظة بلحظة.\n\n"
                
                message += f"📍 **المصدر:** {source_name}"
                
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
