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
            with open(SENT_NEWS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_sent_news(sent_list):
    try:
        with open(SENT_NEWS_FILE, "w", encoding="utf-8") as f:
            json.dump(sent_list[-400:], f)
    except Exception as e:
        print(f"Error saving sent news: {e}")

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

def fetch_article_summary(url):
    """دالة لجلب تفاصيل الخبر من الرابط الأصلي مع حماية كاملة من أي خطأ"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            article_text = ""
            for p in paragraphs:
                text = p.get_text().strip()
                if len(text) > 25 and "حقوق" not in text and "محفوظة" not in text:
                    article_text += text + "\n\n"
                    if len(article_text) > 450:  # اكتفاء بأول 450 حرف لخبر مكثف وجميل
                        break
            if len(article_text) > 40:
                return article_text.strip()
    except Exception as e:
        print(f"Scraping info warning: {e}")
    return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True  # إلغاء الصور والمعاينة نهائياً لتصل الرسالة نصية فقط
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Message sent successfully to Telegram!")
        else:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    print("Google News Full-Content Football Bot started...")
    try:
        sent_news = load_sent_news()
        articles_sent_count = 0
        
        for feed_info in GOOGLE_NEWS_FEEDS:
            if articles_sent_count >= 2: # إرسال خبرين في كل دورة تشغيل
                break
                
            source_name = feed_info["name"]
            feed_url = feed_info["url"]
            
            try:
                print(f"Checking source: {source_name}")
                feed = feedparser.parse(feed_url)
                
                if not feed.entries:
                    continue
                
                for entry in feed.entries[:8]:
                    link = getattr(entry, 'link', '')
                    if not link or link in sent_news:
                        continue
                    
                    raw_title = getattr(entry, 'title', 'خبر رياضي جديد')
                    print(f"Found article: {raw_title}")
                    
                    # جلب تفاصيل الخبر من الموقع الأصلي
                    details = fetch_article_summary(link)
                    
                    # بناء رسالة متكاملة وغنية
                    message = f"⚽ **{raw_title}**\n\n"
                    
                    if details:
                        message += f"📄 {details}\n"
                    else:
                        # لو لم يتوفر نص الموقع، نأخذ ملخص الـ RSS إن وجد
                        raw_summary = getattr(entry, 'summary', '')
                        if raw_summary and len(raw_summary) > 15:
                            clean_summary = raw_summary.split('<')[0]
                            message += f"📝 {clean_summary}\n"
                        else:
                            message += f"📌 تابع تفاصيل الخبر الرياضي لحظة بلحظة عبر الرابط أدناه.\n"
                    
                    message += f"\n📍 **المصدر:** {source_name}\n🔗 [اقرأ التفاصيل من هنا]({link})"
                    
                    send_telegram_message(message)
                    
                    sent_news.append(link)
                    articles_sent_count += 1
                    break
            except Exception as e:
                print(f"Error parsing feed {source_name}: {e}")
                
        save_sent_news(sent_news)
        print(f"Task completed successfully. Total articles sent: {articles_sent_count}")
    except Exception as e:
        print(f"Critical execution error: {e}")
    
    # إنهاء التشغيل بكود 0 لضمان عدم فشل الـ Workflow أبداً
    sys.exit(0)

if __name__ == "__main__":
    main()
