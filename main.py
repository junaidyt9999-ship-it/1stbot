import os
import threading
import time
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ১. ফেক ওয়েব সার্ভার (Render-কে সচল রাখার জন্য)
app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 Bot is running flawlessly with Premium UI!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ২. টেলিগ্রাম বটের মূল কনফিগারেশন
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN variable not found in environment!")

bot = telebot.TeleBot(BOT_TOKEN)

# কমন ইনলাইন বাটন জেনারেটর (চ্যানেল সাপোর্ট ও ডেভেলপার ক্রেডিট)
def get_welcome_buttons():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("📢 Official Channel", url="https://t.me/JHx_Technical_Creator"),
        InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/Akram_99360")
    )
    return markup

# ডেটা রিফ্রেশ/লোডিং বাটন
def get_refresh_button(action_type):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔄 Refresh Data", callback_data=f"refresh_{action_type}"))
    return markup

# 👑 /start বা /help কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "✨ **Welcome to Premium ID Finder Service** ✨\n\n"
        "⚡ *Fast, Secure & Always Online.*\n\n"
        "📥 **How to use:**\n"
        "├ 💬 *Send any text* to fetch your own ID.\n"
        "└ 🔀 *Forward any message* (User/Channel/Group) to extract its metadata.\n\n"
        "💎 *Powered by JHx Technical Creator*"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=get_welcome_buttons())

# 👤 নরমাল মেসেজের ক্ষেত্রে (নিজের আইডি খোঁজা)
@bot.message_handler(func=lambda message: not message.forward_date)
def send_user_id(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "❌ None"
    
    response = (
        "👑 **PREMIUM USER PROFILE** 👑\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Name:** `{first_name}`\n"
        f"🌐 **Username:** {username}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Status: Active*"
    )
    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=get_refresh_button("user"))

# 📢 ফরওয়ার্ড করা মেসেজের ক্ষেত্রে (অন্যদের আইডি খোঁজা)
@bot.message_handler(func=lambda message: message.forward_date is not None)
def send_forwarded_id(message):
    # যদি কোনো ইউজার থেকে ফরওয়ার্ড করা হয়
    if message.forward_from:
        f_id = message.forward_from.id
        f_name = message.forward_from.first_name
        username = f"@{message.forward_from.username}" if message.forward_from.username else "❌ None"
        
        response = (
            "🎯 **FORWARDED TARGET DETAILS** 🎯\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✨ **Type:** `User / Client`\n"
            f"👤 **Name:** `{f_name}`\n"
            f"🌐 **Username:** {username}\n"
            f"🆔 **Target ID:** `{f_id}`\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
    
    # যদি কোনো চ্যানেল বা গ্রুপ থেকে ফরওয়ার্ড করা হয়
    elif message.forward_from_chat:
        f_id = message.forward_from_chat.id
        f_title = message.forward_from_chat.title
        f_type = message.forward_from_chat.type
        username = f"@{message.forward_from_chat.username}" if message.forward_from_chat.username else "❌ Public Link Unavailable"
        
        response = (
            "📢 **FORWARDED SOURCE DETAILS** 📢\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ **Type:** `{f_type.capitalize()}`\n"
            f"📛 **Title:** `{f_title}`\n"
            f"🌐 **Username/Link:** {username}\n"
            f"🆔 **Source ID:** `{f_id}`\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
    
    # ফরওয়ার্ড প্রাইভেসির কারণে আইডি না পাওয়া গেলে
    else:
        response = (
            "⚠️ **PRIVACY RESTRICTION ALERT** ⚠️\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔒 This user has enabled *Forwarded Messages Privacy*.\n"
            "❌ Telegram API cannot extract the exact ID from this message."
        )

    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=get_refresh_button("forward"))

# 🔄 ইনলাইন লোডিং ও রিফ্রেশিং অ্যানিমেশন সিস্টেম (Callback Query)
@bot.callback_query_handler(func=lambda call: call.data.startswith('refresh_'))
def handle_refresh(call):
    try:
        # ১. লোডিং স্টেট অ্যানিমেশন দেখানো (ইউজার বাটনে ক্লিক করলে রিয়েল-টাইম লোডিং ফিল পাবে)
        bot.answer_callback_query(call.id, text="⚡ Loading latest data from Telegram API...", show_alert=False)
        
        current_text = call.message.text
        
        # টেক্সটের শেষে একটি টাইমস্ট্যাম্প বা লোডিং সাইন অ্যাড করে এডিট করা
        loading_text = current_text + "\n\n🔄 *Refreshing sync...*"
        bot.edit_message_text(loading_text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
        
        # একটি ছোট রিয়েলস্টিক পজ/ডিলে জেনারেট করা
        time.sleep(1)
        
        # ২. সাকসেস মেসেজ পুশ করা
        bot.answer_callback_query(call.id, text="✅ Data Sync Complete! Up-to-date.", show_alert=False)
        
        # মূল মেসেজটিকে আগের সুন্দর অবস্থায় ফিরিয়ে নিয়ে আসা
        bot.edit_message_text(current_text, call.message.chat.id, call.message.message_id, parse_mode='Markdown', reply_markup=get_refresh_button("user" if "PROFILE" in current_text else "forward"))
        
    except Exception as e:
        # যদি ডেটাতে কোনো পরিবর্তন না থাকে তবে এরর এড়ানো
        bot.answer_callback_query(call.id, text="✅ Data is already up-to-date!")

if __name__ == "__main__":
    # ব্যাকগ্রাউন্ড থ্রেডে ফ্ল্যাক্স সার্ভার চালু করা
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("💎 Premium Bot is now running...")
    bot.infinity_polling()
