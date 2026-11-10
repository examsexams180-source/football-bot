import os
import requests
import sys
import json
from bs4 import BeautifulSoup

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
            print("Direct news sent successfully!")
        else:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

def scrape_yallakora():
    """دالة تسحب الأخبار مباشرة من موقع يلا كورة دون الحاجة لأي RSS"""
    news_list = []
    url = "https://www.yallakora.com/match-center" # أو صفحة الأخبار الرئيسية
    # سنستخدم صفحة الأخبار المباشرة لتفادي أي حظر
    news_url = "https://www.yallakora.com/news"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(news_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # البحث عن عناصر الأخبار في صفحة يلا كورة
            # (نستهدف الروابط والعناوين داخل أقسام الأخبار بالموقع)
            articles = soup.find_all('div', class_='story-item') or soup.find_all('a', class_='news-item')
            
            if not articles:
                # طريقة بديلة عامة لأي روابط أخبار في الصفحة
                articles = soup.find_all('a', href=True)
                
            for item in articles[:20]:
                try:
                    # استخراج العنوان والرابط
                    if item.name == 'a':
                        link = item['href']
                        title = item.get_text().strip()
                    else:
                        a_tag = item.find('a', href=True)
                        if not a_tag:
                            continue
                        link = a_tag['href']
                        title = a_tag.get_text().strip()
                    
                    if not link.startswith('http'):
                        link = "https://www.yallakora.com" + link
                        
                    if len(title) > 20 and "رابط" not in title and "المزيد" not in title:
                        news_list.append({"title": title, "link": link})
                except:
                    continue
    except Exception as e:
        print(f"Scraping error: {e}")
        
    return news_list

def main():
    print("Direct Web Scraping Bot started...")
    try:
        sent_news = load_sent_news()
        articles_sent_count = 0
        
        # جلب الأخبار مباشرة من الموقع
        fetched_news = scrape_yallakora()
        
        for article in fetched_news:
            if articles_sent_count >= 2: # إرسال خبرين في كل دورة
                break
                
            title = article["title"]
            link = article["link"]
            
            if link in sent_news:
                continue
                
            # بناء رسالة نظيفة واحترافية
            message = f"⚽ **{title}**\n\n"
            message += f"📌 **المصدر:** موقع يلا كورة - YallaKora\n"
            message += f"🔗 [اقرأ التفاصيل من هنا]({link})"
            
            send_telegram_message(message)
            
            sent_news.append(link)
            articles_sent_count += 1
            
        save_sent_news(sent_news)
        print(f"Task completed. Total direct articles sent: {articles_sent_count}")
    except Exception as e:
        print(f"Critical error: {e}")
        
    sys.exit(0)

if __name__ == "__main__":
    main()
