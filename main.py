import os
import time
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

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

def zh(text):
    try:
        return GoogleTranslator(
            source='auto',
            target='zh-CN'
        ).translate(text)
    except:
        return "翻译失败"

def check(feed_url, source):
    global sent

    feed = feedparser.parse(feed_url)

    if not feed.entries:
        return

    latest = feed.entries[0]

    title = latest.title
    link = latest.link

    uid = link

    if uid in sent:
        return

    sent.add(uid)

    if len(sent) > 200:
        sent = set(list(sent)[-100:])

    save_sent(sent)

    chinese = zh(title)

    msg = f'''
{source} 更新

原文：
{title}

中文：
{chinese}

链接：
{link}
'''

    send_tg(msg)

print("Bot started")

check(X_RSS, "🇺🇸 X")
check(TRUTH_RSS, "🟦 Truth")
