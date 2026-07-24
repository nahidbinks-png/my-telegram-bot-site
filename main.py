import os
import telebot

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(message, "হাল্লো! আমি অনলাইনে আছি এবং ২৪ ঘণ্টা কাজ করছি! 🚀")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
  bot.reply_to(message, f"তুমি বলেছ: {message.text}")


print("Bot is running...")
bot.infinity_polling()
