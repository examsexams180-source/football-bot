import os
import requests
import feedparser
import sys
import json
from html.parser import HTMLParser

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
    except:
        pass

class HTMLTextExtractor(HTMLParser):
    """أداة نظيفة لإزالة أكواد HTML والحصول على النص الحقيقي فقط بدون تأليف"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.text = []

    def handle_data(self, d):
        self.text.append(d)

    def get_data(self):
        return ''.join(self.text).strip()

def clean_html(raw_html):
    if not raw_html:
        return ""
    try:
        parser = HTMLTextExtractor()
        parser.feed(raw_html)
        return parser.get_data()
    except:
        return raw_html.split('<')[0].strip()

# مصادر Google News RSS المتقدمة (تستخرج الأخبار مع ملخصاتها الحقيقية من كبرى المواقع)
GOOGLE_NEWS_FEEDS = [
    {
        "name": "أخبار كرة القدم العالمية والمحلية",
        "url": "https://news.google.com/rss/search?q=%D9%83%D8%B1%D8%A9+%D9%82%D8%AF%D9%85&hl=ar&gl=EG&ceid=EG:ar"
    },
    {
        "name": "موقع بطولات - Btolat",
        "url": "https://news.google.com/rss/search?q=site:btolat.com+%D9%83%D8%B1%D8%A9+%D9%82%D8%AF%D9%85&hl=ar&gl=EG&ceid=EG:ar"
    },
    {
        "name": "موقع يلا كورة - YallaKora",
        "url": "https://news.google.com/rss/search?q=site:yallakora.com+%D9%83%D8%B1%D8%A9+%D9%82%D8%AF%D9%85&hl=ar&gl=EG&ceid=EG:ar"
    },
    {
        "name": "الدوري المصري والبطولات العربية",
        "url": "https://news.google.com/rss/search?q=%D8%A7%D9%84%D8%AF%D9%88%D8%B1%D9%8A+%D8%A7%D9%84%D9%85%D8%B5%D8%B1%D9%8A+OR+%D8%A7%D9%84%D8%B2%D9%85%D8%A7%D9%84%D9%83+OR+%D8%A7%D9%84%D8%A3%D9%87%D目前的+OR+%D8%A7%D9%84%D8%A3%D9%87%D9%84%D9%8A&hl=ar&gl=EG&ceid=EG:ar"
    }
]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True  # إلغاء معاينة الصور والروابط تماماً
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Google News article sent successfully!")
        else:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    print("Google News Football Bot started...")
    try:
        sent_news = load_sent_news()
        articles_sent_count = 0
        
        for feed_info in GOOGLE_NEWS_FEEDS:
            if articles_sent_count >= 2: # إرسال خبرين في كل دورة تشغيل لضمان استمرارية التحديث
                break
                
            source_name = feed_info["name"]
            feed_url = feed_info["url"]
            
            try:
                print(f"Checking source: {source_name}")
                feed = feedparser.parse(feed_url)
                
                if not feed.entries:
                    continue
                
                for entry in feed.entries[:10]:
                    link = getattr(entry, 'link', '')
                    if not link or link in sent_news:
                        continue
                    
                    title = getattr(entry, 'title', '').strip()
                    if not title:
                        continue
                    
                    # استخراج الملخص الحقيقي من وصف جوجل نيوز
                    raw_summary = getattr(entry, 'summary', getattr(entry, 'description', ''))
                    clean_summary = clean_html(raw_summary)
                    
                    # بناء رسالة متكاملة وغنية بالتفاصيل الحقيقية
                    message = f"⚽ **{title}**\n\n"
                    
                    # إذا جلبنا ملخصاً حقيقياً وواضحاً من جوجل، نضيفه للرسالة
                    if clean_summary and len(clean_summary) > 30 and clean_summary != title:
                        if len(clean_summary) > 400:
                            clean_summary = clean_summary[:400] + "..."
                        message += f"📝 {clean_summary}\n\n"
                    
                    message += f"📌 **المصدر:** {source_name}\n🔗 [اقرأ التفاصيل من هنا]({link})"
                    
                    send_telegram_message(message)
                    
                    sent_news.append(link)
                    articles_sent_count += 1
                    break
            except Exception as e:
                print(f"Error parsing feed {source_name}: {e}")
                
        save_sent_news(sent_news)
        print(f"Task completed. Total articles sent: {articles_sent_count}")
    except Exception as e:
        print(f"Critical error: {e}")
    
    sys.exit(0)

if __name__ == "__main__":
    main()
