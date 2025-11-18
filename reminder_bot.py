import os
import asyncio
from datetime import datetime
import dateparser
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

# Store reminders in memory
user_reminders = {}

# Check reminders loop
async def reminder_checker():
    while True:
        now = datetime.now()
        for user_id, reminders in list(user_reminders.items()):
            for r in reminders[:]:
                if now >= r["when"]:
                    try:
                        await r["context"].bot.send_message(
                            chat_id=user_id,
                            text=f"⏰ *Lembrete:* {r['text']}",
                            parse_mode="Markdown"
                        )
                    except Exception:
                        pass
                    reminders.remove(r)
        await asyncio.sleep(30)


# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Olá! Eu sou seu bot de lembretes. ⏰\n\n"
        "Use o comando:\n"
        "`/lembre <quando> ; <mensagem>`\n\n"
        "Exemplos:\n"
        "`/lembre amanhã às 9h ; beber água`\n"
        "`/lembre 25 de dezembro às 08:00 ; presente de natal`\n"
        "`/listar` para ver seus lembretes.\n"
        "`/apagar <número>` para remover um lembrete."
    )

    await update.message.reply_markdown(msg)


# Create reminder
async def lembre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/lembre", "").strip()

    if ";" not in text:
        await update.message.reply_text(
            "Formato inválido.\nUse: /lembre <quando> ; <mensagem>"
        )
        return

    when_text, reminder_text = map(str.strip, text.split(";", 1))
    when = dateparser.parse(when_text, languages=["pt"])

    if not when:
        await update.message.reply_text("Não consegui entender a data. Tente outro formato.")
        return

    user_id = update.effective_user.id
    if user_id not in user_reminders:
        user_reminders[user_id] = []

    user_reminders[user_id].append({
        "when": when,
        "text": reminder_text,
        "context": context
    })

    await update.message.reply_text(
        f"⏰ Lembrete salvo!\n\n*Quando:* {when.strftime('%d/%m/%Y %H:%M')}\n*Mensagem:* {reminder_text}",
        parse_mode="Markdown"
    )


# List reminders
async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reminders = user_reminders.get(update.effective_user.id, [])
    if not reminders:
        await update.message.reply_text("Você não tem lembretes salvos.")
        return

    msg = "📋 *Here are your current reminders:*"
    for i, r in enumerate(reminders, 1):
        msg += f"\n{i}. ⏰ {r['text']} — `{r['when'].strftime('%d/%m/%Y %H:%M')}`"

    await update.message.reply_markdown(msg)


# Delete reminder
async def apagar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        index = int(update.message.text.split(" ")[1]) - 1
    except:
        await update.message.reply_text("Use: /apagar <número do lembrete>")
        return

    reminders = user_reminders.get(update.effective_user.id, [])

    if index < 0 or index >= len(reminders):
        await update.message.reply_text("Número inválido.")
        return

    removed = reminders.pop(index)

    await update.message.reply_text(f"❌ Lembrete removido: {removed['text']}")


# Main
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lembre", lembre))
    app.add_handler(CommandHandler("listar", list_reminders))
    app.add_handler(CommandHandler("apagar", apagar))

    asyncio.create_task(reminder_checker())

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
