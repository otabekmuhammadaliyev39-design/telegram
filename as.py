#!/usr/bin/env python3
# FINAL COMMENT USERBOT + REAL MS LOG (RAILWAY READY)

import asyncio
import os
import time
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# =============== API (ENV) =================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

# =============== FILES =====================
STATE_FILE = "commented_posts.txt"
CONFIG_FILE = "config.txt"

# =============== DEFAULTS ==================
DEFAULT_GROUP = "@Diary_o1chat"
DEFAULT_COMMENT = ".."

# =============== CLIENT ====================
client = TelegramClient(
    StringSession(SESSION_STRING),
    API_ID,
    API_HASH,
    sequential_updates=False
)

ENABLED = False
GROUP = DEFAULT_GROUP
COMMENT = DEFAULT_COMMENT
commented = set()

# =============== CONFIG ====================
def load_config():
    global GROUP, COMMENT
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            if len(lines) >= 2:
                GROUP, COMMENT = lines[0], lines[1]

def save_config():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(f"{GROUP}\n{COMMENT}\n")

def load_posts():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            for x in f:
                if x.strip().isdigit():
                    commented.add(int(x.strip()))

def save_post(pid):
    with open(STATE_FILE, "a") as f:
        f.write(f"{pid}\n")

# =============== SAVED MESSAGES CONTROL =================
@client.on(events.NewMessage(outgoing=True))
async def control(event):
    global ENABLED, GROUP, COMMENT

    if not (event.is_private and event.out):
        return

    text = event.raw_text.strip().lower()

    if text == "on":
        ENABLED = True
        await event.reply("✅ BOT YOQILDI")

    elif text == "off":
        ENABLED = False
        await event.reply("⛔ BOT O‘CHDI")

    elif text == "status":
        await event.reply(
            f"📊 Holat: {'ON' if ENABLED else 'OFF'}\n"
            f"👥 Group: {GROUP}\n"
            f"💬 Comment: {COMMENT}\n"
            f"🧠 Postlar: {len(commented)}"
        )

    elif text.startswith("setgroup "):
        GROUP = event.raw_text.split(" ", 1)[1].strip()
        commented.clear()
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        save_config()
        await event.reply(f"👥 Group o‘zgardi → {GROUP}")

    elif text.startswith("setcomment "):
        COMMENT = event.raw_text.split(" ", 1)[1]
        save_config()
        await event.reply("💬 Comment o‘zgardi")

    elif text == "clear":
        commented.clear()
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        await event.reply("🗑 Tarix tozalandi")

# =============== GROUP HANDLER =================
@client.on(events.NewMessage())
async def handler(event):
    if not ENABLED:
        return

    if not event.chat or not event.chat.username:
        return

    if f"@{event.chat.username.lower()}" != GROUP.lower():
        return

    if not event.fwd_from or event.fwd_from.channel_post is None:
        return

    if event.id in commented:
        return

    post_time = time.perf_counter()
    post_clock = datetime.now().strftime("%H:%M:%S.%f")[:-3]

    try:
        await event.reply(COMMENT)
        reply_time = time.perf_counter()
        reply_clock = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        delay_ms = (reply_time - post_time) * 1000

        commented.add(event.id)
        save_post(event.id)

        print(
            f"\n📨 Post keldi      : {post_clock}"
            f"\n💬 Reply yuborildi : {reply_clock}"
            f"\n⏱ Delay           : {delay_ms:.1f} ms"
            f"\n{'-'*40}"
        )

    except Exception as e:
        print("❌ Xato:", e)

# =============== MAIN =================
async def main():
    load_config()
    load_posts()
    await client.start()
    print("🚀 COMMENT USERBOT ISHLAYAPTI (RAILWAY)")
    await client.run_until_disconnected()

asyncio.run(main())
