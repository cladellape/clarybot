# Reminder Telegram Bot

This is a template repository for a Telegram reminder bot built with Python,
APScheduler, dateparser, and python-telegram-bot.

## Structure
- reminder_bot.py — main bot script
- requirements.txt — dependencies
- README.md — instructions

## Running locally
```
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=YOUR_TOKEN
python reminder_bot.py
```

## Deploy on Render
1. Upload this repo to GitHub
2. Create a new Render Web Service
3. Set start command:
```
python reminder_bot.py
```
4. Add env var:
```
TELEGRAM_BOT_TOKEN=your_token
```
