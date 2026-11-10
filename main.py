import os
import requests
import feedparser
import sys
import json
import google.generativeai as genai
from html.parser import HTMLParser

# بيانات التيليجرام الخاصة بك
TELEGRAM_BOT_TOKEN = "9113301542:AAGAltyA38C8YTJWeFPf1PtnuVY40PaC0cE"
TELEGRAM_CHAT_ID = "-1003976750898"

# مفتاح جيميناي
GEMINI_API_KEY = "AQ.Ab8RN6KgXzmVV1fNVwV5g3WHDv5qiuXz_jGB5BeUZc-MKWyUug"
genai.configure(api_key=GEMINI_API_KEY)

# ملف حفظ الروابط المرسلة لمنع التكرار نهائياً
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

# مصادر الأخبار الرياضية العربية عبر Google News RSS لالتقاط أحدث العناوين فور نزولها
NEWS_FEEDS = [
    {
        "name": "موقع بطولات - Btolat",
        "url": "https://news.google.com/rss/search?q=site:btolat.com+%D9%83%D8%B1%D8%A9+%D9%82%D8%AF%D9%85&hl=ar&gl=EG&ceid=EG:ar"
    },
    {
        "name": "موقع يلا كورة - YallaKora",
        "url": "https://news.google.com/rss/search?q=site:yallakora.com+%D9%83%D8%B1%D8%A9+%D9%82%D8%AF%D9%85&hl=ar&gl=EG&ceid=EG:ar"
    },
    {
        "name": "أخبار كرة القدم العربية والعالمية",
        "url": "https://news.google.com/rss/search?q=%D9%83%D8%B1%D8%A9+%D9%82%D8%AF%D9%85&hl=ar&gl=EG&ceid=EG:ar"
    }
]

def generate_ai_news_details(title):
    """جعل جيميناي يبحث بنفسه على شبكة الإنترنت ويستخلص تفاصيل الخبر بالكامل"""
    try:
        # تفعيل أداة البحث المباشر لجيميناي (Google Search Grounding)
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[{"google_search": {}}]
        )
        
        prompt = f"""
أنت محرر رياضي محترف. بناءً على هذا العنوان الإخباري: "{title}"
قم بالبحث في الإنترنت عن تفاصيل هذا الخبر الحقيقية، ثم اكتب فقرة إخبارية متكاملة، احترافية، وواضحة باللغة العربية الفصحى تشرح تفاصيل الخبر والملابسات المحيطة به.
الشروط الصارمة:
1. ممنوع تماماً تأليف أي أحداث وهمية أو غير حقيقية.
2. اعتمد على الحقائق الرياضية الدقيقة من نتائج البحث.
3. اجعل النص في حدود 3 إلى 4 أسطر مكثفة وممتعة للقارئ على تيليجرام.
4. لا تكرر العنوان بالحرف بل ادخل في التفاصيل مباشرة.
"""
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        print(f"Gemini Search & API Error: {e}")
    return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            print("Full AI-searched news sent successfully to Telegram!")
        else:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    print("Full AI Search Football Bot started...")
    try:
        sent_news = load_sent_news()
        articles_sent_count = 0
        
        for feed_info in NEWS_FEEDS:
            if articles_sent_count >= 2: # إرسال خبرين مفصلين بالكامل في كل دورة
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
                    
                    # جيميناي يبحث الآن بنفسه على الإنترنت ويجلب التفاصيل الكاملة
                    print(f"Gemini is searching and summarizing for: {title}")
                    ai_details = generate_ai_news_details(title)
                    
                    # بناء الرسالة النهائية المتكاملة
                    message = f"⚽ **{title}**\n\n"
                    
                    if ai_details and ai_details.strip() != title.strip():
                        message += f"📝 {ai_details}\n\n"
                        
                    message += f"📌 **المصدر:** {source_name}\n🔗 [اقرأ التفاصيل من هنا]({link})"
                    
                    send_telegram_message(message)
                    
                    sent_news.append(link)
                    articles_sent_count += 1
                    break
            except Exception as e:
                print(f"Error parsing feed {source_name}: {e}")
                
        save_sent_news(sent_news)
        print(f"Task completed. Total AI searched articles sent: {articles_sent_count}")
    except Exception as e:
        print(f"Critical error: {e}")
    
    sys.exit(0)

if __name__ == "__main__":
    main()
