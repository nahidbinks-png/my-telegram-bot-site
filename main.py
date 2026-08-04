import os
import telebot
from telebot import types
from supabase import create_client, Client
from flask import Flask
import threading

# এনভায়রনমেন্ট ভ্যারিয়েবল থেকে টোকেন এবং ডাটাবেজ তথ্য নেওয়া
BOTTOKEN = os.environ.get('BOT_TOKEN')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

bot = telebot.TeleBot(TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ফ্লাস্ক সার্ভার (Render-এ পোর্ট সচল রাখার জন্য)
app = Flask('')

@app.route('/')
def home():
    return "Refer & Earn Bot is running!"

def run_web():
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

# মেইন মেনু কিবোর্ড
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("My Balance Ω"),
        types.KeyboardButton("Refer & Earn 👥"),
        types.KeyboardButton("Set Wallet 💎"),
        types.KeyboardButton("Cash Out 💡")
    )
    return markup

# /start কমান্ড এবং রেফারেল হ্যান্ডলার
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    # রেফারের প্যারামিটার চেক করা (যেমন: /start 123456789)
    args = message.text.split()
    referrer_id = None
    if len(args) > 1:
        try:
            referrer_id = int(args[1])
        except ValueError:
            pass

    # ইউজারের ডেটা ডাটাবেজে আছে কি না চেক করা
    response = supabase.table("users").select("*").eq("user_id", user_id).execute()
    
    if not response.data:
        # নতুন ইউজার হলে ডাটাবেজে সেভ করা
        supabase.table("users").insert({
            "user_id": user_id,
            "balance": 0.0,
            "wallet": "Not Set",
            "referrals": 0
        }).execute()
        
        # যদি কেউ রেফার করে থাকে এবং নিজের লিংকে নিজেই না ঢুকে থাকে
        if referrer_id and referrer_id != user_id:
            ref_check = supabase.table("users").select("*").eq("user_id", referrer_id).execute()
            if ref_check.data:
                # রেফারারের ব্যালেন্স এবং রেফার কাউন্ট বাড়ানো (যেমন: ১ টাকা করে)
                old_balance = ref_check.data[0]['balance']
                old_refs = ref_check.data[0]['referrals']
                
                supabase.table("users").update({
                    "balance": old_balance + 1.0,
                    "referrals": old_refs + 1
                }).eq("user_id", referrer_id).execute()
                
                # রেফারারকে নোটিফিকেশন পাঠানো
                try:
                    bot.send_message(
                        referrer_id, 
                        "💰 আপনার ব্যালেন্সে ১ টাকা যোগ করা হয়েছে 💰"
                    )
                except:
                    pass

    bot.send_message(
        message.chat.id, 
        f"👋 Hello, 🇧🇩\n**{first_name}** 🇧🇩!\n\n📢 Join All Channels To Continue.",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# বাটন হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text
    user_id = message.from_user.id
    
    # ডেটাবেজ থেকে ইউজারের তথ্য আনা
    res = supabase.table("users").select("*").eq("user_id", user_id).execute()
    user_data = res.data[0] if res.data else {"balance": 0.0, "wallet": "Not Set", "referrals": 0}

    if text == "My Balance Ω":
        bot.reply_to(message, f"💳 Your Balance: {user_data['balance']} টাকা\n👥 Total Referrals: {user_data['referrals']}")

    elif text == "Refer & Earn 👥":
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        
        msg = (
            f"🏅 Per Referral: 1 টাকা\n\n"
            f"🔗 Your Referral Link: {ref_link}\n\n"
            f"📊 Your Total Referrals: {user_data['referrals']} টি\n\n"
            f"🚫 Fake and cheat referrals will not be paid"
        )
        bot.reply_to(message, msg)

    elif text == "Set Wallet 💎":
        msg = bot.reply_to(message, "📝 আপনার বিকাশ/নগদ নম্বরটি লিখে পাঠান:")
        bot.register_next_step_handler(msg, save_wallet)

    elif text == "Cash Out 💡":
        balance = user_data['balance']
        if balance < 10:
            bot.reply_to(message, "⚠️ আপনার ব্যালেন্স কম আছে। আপনার টাকা উত্তোলনের জন্য কমপক্ষে আপনার ব্যালেন্সে 10 টাকা থাকতে হবে ⚠️")
        else:
            bot.reply_to(message, f"✅ আপনার উইথড্র রিকোয়েস্ট সফলভাবে জমা হয়েছে! বর্তমান ওয়ালেট: {user_data['wallet']}")

def save_wallet(message):
    user_id = message.from_user.id
    wallet_no = message.text
    
    supabase.table("users").update({"wallet": wallet_no}).eq("user_id", user_id).execute()
    bot.reply_to(message, f"✅ আপনার ওয়ালেট সফলভাবে সেভ হয়েছে: {wallet_no}", reply_markup=main_menu())

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.start()
    
    print("Refer Bot is running...")
    bot.infinity_polling()
    
