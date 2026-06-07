import os
import telebot

# Render-এর Environment Variable থেকে টোকেনটি নেওয়া হবে
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN variable not found in environment!")

bot = telebot.TeleBot(BOT_TOKEN)

# /start বা /help কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 **Welcome to User ID Finder Bot!**\n\n"
        "📩 Send me any message to get your Telegram User ID.\n"
        "🔀 Forward a message from any user or channel to get their ID!"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

# যেকোনো নরমাল মেসেজ দিলে নিজের আইডি দেখাবে
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

# কোনো মেসেজ ফরওয়ার্ড করলে সেই ইউজার/চ্যানেল/গ্রুপের আইডি দেখাবে
@bot.message_handler(func=lambda message: message.forward_date is not None)
def send_forwarded_id(message):
    # যদি কোনো ইউজার থেকে ফরওয়ার্ড করা হয়
    if message.forward_from:
        f_id = message.forward_from.id
        f_name = message.forward_from.first_name
        response = f"👤 **Forwarded User Info:**\n🔹 **Name:** {f_name}\n🆔 **ID:** `{f_id}`"
    
    # যদি কোনো চ্যানেল থেকে ফরওয়ার্ড করা হয়
    elif message.forward_from_chat:
        f_id = message.forward_from_chat.id
        f_title = message.forward_from_chat.title
        f_type = message.forward_from_chat.type
        response = f"📢 **Forwarded {f_type.capitalize()} Info:**\n🔹 **Title:** {f_title}\n🆔 **ID:** `{f_id}`"
    
    # যদি ইউজারের প্রাইভেসি সেটিংস অন থাকে (নাম দেখাবে কিন্তু আইডি সরাসরি পাওয়া যায় না)
    else:
        response = "⚠️ **Privacy Alert:** This user has hidden their account link when forwarding messages, so the ID could not be fetched."

    bot.reply_to(message, response, parse_mode='Markdown')

# বট রান করার কমান্ড
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()