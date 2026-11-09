import os
import requests
import feedparser
import sys

# بيانات التيليجرام ومفتاح Grok الخاص بك
TELEGRAM_BOT_TOKEN = "9113301542:AAGAltyA38C8YTJWeFPf1PtnuVY40PaC0cE"
TELEGRAM_CHAT_ID = "-1003976750898"
GROK_API_KEY = "grok_597c29bf36d4744f2978f187039eac33_308f81e4e270c35caf567b540c75aed24d8f82ae45fbeac50638882a87791e0c"

def test_grok_directly():
    """دالة لاختبار مفتاح وخدمة Grok API بشكل مباشر ومفصل"""
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "grok-2",
        "messages": [
            {"role": "system", "content": "أنت مساعد ذكي."},
            {"role": "user", "content": "اكتب جملة قصيرة جداً تثبت أنك تعمل بشكل صحيح باللغة العربية."}
        ],
        "temperature": 0.7
    }
    
    print("--- بدء اختبار اتصال Grok API ---")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            reply = data["choices"][0]["message"]["content"].strip()
            print(f"✅ نجح الاتصال بـ Grok! الرد كان: {reply}")
            return reply
        else:
            print(f"❌ فشل الاتصال بـ Grok. الكود: {response.status_code}")
    except Exception as e:
        print(f"❌ حدث خطأ استثنائي أثناء الاتصال: {e}")
    print("--- نهاية اختبار الاتصال ---")
    return None

def main():
    print("Grok diagnostic test started...")
    
    # إجراء اختبار مباشر لـ Grok وطباعة النتيجة في السجلات
    grok_response = test_grok_directly()
    
    # إرسال رسالة تجريبية لتيليجرام تخبرنا بحالة الاختبار
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    status_msg = f"🧪 **تقرير اختبار البوت:**\n\nرد الذكاء الاصطناعي (Grok):\n`{grok_response}`"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": status_msg,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)
    
    print("Test task completed. Exiting.")

if __name__ == "__main__":
    main()
    sys.exit(0)
