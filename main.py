import os
import requests
import sys
import json

# بيانات التيليجرام الخاصة بك
TELEGRAM_BOT_TOKEN = "9113301542:AAGAltyA38C8YTJWeFPf1PtnuVY40PaC0cE"
TELEGRAM_CHAT_ID = "-1003976750898"

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

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True  # منع الصور والمعاينة نهائياً
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("News sent successfully to Telegram!")
        else:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

def fetch_sports_news():
    """جلب أخبار كرة القدم من مصدر برمجي موثوق ومستقر 100% بدون حظر"""
    articles = []
    try:
        # استخدام مصدر بيانات رياضي عالمي وموثوق يزودنا بأحدث الأخبار الحقيقية
        url = "https://www.thesportsdb.com/api/v1/json/3/searchevents.php?e=Soccer" # أو نقطة بيانات أخبار بديلة
        # ولضمان الحصول على أخبار رياضية حية ومتنوعة باللغة العربية، سنستخدم مصدر بيانات Open API موثوق:
        news_api_url = "https://newsdata.io/api/1/news?apikey=pub_fakesample&category=sports&language=ar"
        
        # بما أننا نريد مصدراً مجانياً بالكامل ولا يتطلب مفاتيح معقدة قد تنتهي، سنعتمد على نقطة بيانات رياضية مباشرة:
        free_endpoint = "https://site.api.espn.com/apis/site/v2/sports/soccer/all/news"
        
        response = requests.get(free_endpoint, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            items = data.get("articles", [])
            for item in items[:10]:
                headline = item.get("headline", "")
                description = item.get("description", "")
                link_list = item.get("links", [])
                link = "https://www.espn.com/soccer/"
                if link_list:
                    try:
                        link = link_list[0]["href"]
                    except:
                        pass
                
                if headline:
                    articles.append({
                        "title": headline,
                        "summary": description,
                        "link": link,
                        "source": "ESPN Sports News"
                    })
    except Exception as e:
        print(f"API fetch error: {e}")
        
    return articles

def main():
    print("Reliable Sports Bot started...")
    try:
        sent_news = load_sent_news()
        articles_sent_count = 0
        
        fetched_news = fetch_sports_news()
        
        for article in fetched_news:
            if articles_sent_count >= 2: # إرسال خبرين في كل دورة
                break
                
            title = article["title"]
            summary = article["summary"]
            link = article["link"]
            source = article["source"]
            
            if link in sent_news:
                continue
                
            # بناء رسالة نظيفة واحترافية متكاملة
            message = f"⚽ **{title}**\n\n"
            
            if summary and len(summary) > 15:
                message += f"📝 {summary}\n\n"
                
            message += f"📌 **المصدر:** {source}\n"
            message += f"🔗 [اقرأ التفاصيل من هنا]({link})"
            
            send_telegram_message(message)
            
            sent_news.append(link)
            articles_sent_count += 1
            
        save_sent_news(sent_news)
        print(f"Task completed. Total articles sent: {articles_sent_count}")
    except Exception as e:
        print(f"Critical error: {e}")
        
    sys.exit(0)

if __name__ == "__main__":
    main()
