import os
import threading
from flask import Flask
import telebot

# ১. ফেক ওয়েব সার্ভার তৈরি (রেন্ডারকে শান্ত রাখার জন্য)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running perfectly!"

def run_flask():
    # রেন্ডার ফ্রি সার্ভারে অটোমেটিক একটা PORT এনভায়রনমেন্ট ভ্যারিয়েবল দেয়
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ২. টেলিগ্রাম বটের মূল লজিক
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN variable not found in environment!")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 **Welcome to User ID Finder Bot!**\n\n"
        "📩 Send me any message to get your Telegram User ID.\n"
        "🔀 Forward a message from any user or channel to get their ID!"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: not message.forward_date)
def send_user_id(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "None"
    
    response = (
        "👤 **Your Profile Info:**\n"
        f"🔹 **First Name:** {first_name}\n"
        f"🔹 **Username:** {username}\n"
        f"🆔 **User ID:** `{user_id}`"
    )
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.forward_date is not None)
def send_forwarded_id(message):
    if message.forward_from:
        f_id = message.forward_from.id
        f_name = message.forward_from.first_name
        response = f"👤 **Forwarded User Info:**\n🔹 **Name:** {f_name}\n🆔 **ID:** `{f_id}`"
    elif message.forward_from_chat:
        f_id = message.forward_from_chat.id
        f_title = message.forward_from_chat.title
        f_type = message.forward_from_chat.type
        response = f"📢 **Forwarded {f_type.capitalize()} Info:**\n🔹 **Title:** {f_title}\n🆔 **ID:** `{f_id}`"
    else:
        response = "⚠️ **Privacy Alert:** This user has hidden their account link when forwarding messages."
    bot.reply_to(message, response, parse_mode='Markdown')

if __name__ == "__main__":
    # ওয়েব সার্ভারটিকে আলাদা একটি থ্রেডে ব্যাকগ্রাউন্ডে স্টার্ট করা
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("Bot is running...")
    bot.infinity_polling()
