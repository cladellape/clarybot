import os
import logging
import sqlite3
from datetime import datetime
import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import dateparser

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

conn = sqlite3.connect("reminders.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    time TEXT,
    cron TEXT,
    active INTEGER
)""")
conn.commit()

scheduler = AsyncIOScheduler()

async def send_reminder(user_id, text, app):
    await app.bot.send_message(chat_id=user_id, text=f"⏰ Reminder: {text}")

async def parse_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    user = update.message.from_user.id

    dt = dateparser.parse(msg)
    if dt:
        reminder_text = msg
        c.execute("INSERT INTO reminders (user_id,text,time,cron,active) VALUES (?,?,?,?,?)",
                  (user, reminder_text, dt.isoformat(), None, 1))
        conn.commit()
        reminder_id = c.lastrowid

        scheduler.add_job(send_reminder, "date", run_date=dt,
                          args=[user, reminder_text, context.application],
                          id=str(reminder_id))

        await update.message.reply_text(f"✅ Reminder set for {dt}")
        return

    await update.message.reply_text("❌ Could not understand the date/time.")

async def list_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.id
    rows = c.execute("SELECT id,text,time,cron FROM reminders WHERE user_id=? AND active=1", (user,)).fetchall()
    if not rows:
        await update.message.reply_text("You have no active reminders.")
        return

    out = "📋 Active reminders:\n"
    for r in rows:
        out += f"ID {r[0]} — {r[1]} — {r[2] if r[2] else r[3]}\n"
    await update.message.reply_text(out)

async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rid = context.args[0]
    c.execute("UPDATE reminders SET active=0 WHERE id=?", (rid,))
    conn.commit()

    try:
        scheduler.remove_job(rid)
    except:
        pass

    await update.message.reply_text(f"🗑️ Reminder {rid} cancelled.")

async def help_cmd(update: Update, context):
    await update.message.reply_text(
        "/list — show reminders\n"
        "/cancel <id> — delete a reminder\n"
        "Just send a message with date/time to create a reminder."
    )

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("list", list_cmd))
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, parse_message))

    scheduler.start()
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
