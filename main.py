import os
import json
import feedparser
import requests
from deep_translator import GoogleTranslator

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

X_RSS = "https://rsshub.app/twitter/user/realDonaldTrump"
TRUTH_RSS = "https://truthsocial.com/@realDonaldTrump.rss"
STATE_FILE = "sent.json"

def load_sent():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def save_sent(data):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(data), f)

sent = load_sent()

def send_tg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    print(f"Telegram 响应: {r.status_code} {r.text}")  # ← 新增

def zh(text):
    try:
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except Exception as e:
        print(f"翻译失败: {e}")  # ← 新增
        return "翻译失败"

def check(feed_url, source):
    global sent
    print(f"正在抓取: {feed_url}")  # ← 新增
    feed = feedparser.parse(feed_url)
    print(f"获取到 {len(feed.entries)} 条条目")  # ← 新增
    
    if not feed.entries:
        print(f"❌ {source} RSS 为空，跳过")  # ← 新增
        return
    
    latest = feed.entries[0]
    title = latest.title
    link = latest.link
    uid = link
    print(f"最新条目: {title[:50]}...")  # ← 新增
    
    if uid in sent:
        print(f"已发送过，跳过")  # ← 新增
        return
    
    sent.add(uid)
    if len(sent) > 200:
        sent = set(list(sent)[-100:])
    save_sent(sent)
    
    chinese = zh(title)
    msg = f"{source} 更新\n\n原文：\n{title}\n\n中文：\n{chinese}\n\n链接：\n{link}"
    send_tg(msg)

print("Bot started")
check(X_RSS, "🇺🇸 X")
check(TRUTH_RSS, "🟦 Truth")
print("Bot finished")
