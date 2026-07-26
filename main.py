import os
import telebot
from flask import Flask
import threading
import yt_dlp
from duckduckgo_search import DDGS  # DuckDuckGo সার্চ লাইব্রেরি

# রেন্ডারের এনভায়রনমেন্ট থেকে টোকেন নেওয়া
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# ফ্লাস্ক ওয়েব সার্ভার (Render পোর্ট ওপেন রাখার জন্য)
app = Flask('')

@app.route('/')
def home():
    return "BotSphere is online and running!"

def run_web():
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

# গালি বা খারাপ শব্দের তালিকা
bad_words = [
    "bal", "chudir", "madarchod", "bhenchod", "sala", "shala", "magi", "maggi", 
    "puti", "fokir", "bokachoda", "chodna", "baler", "harami", "haramzada", 
    "kutta", "kuttar baccha", "bastard", "chuda", "chudi", "chudchi", "guda", 
    "gud", "pundir", "shondha", "beshya", "boshi", "banchod", "madrachod", 
    "mc", "bc", "lc", "fc", "gandu", "hijra", "khankir", "khanki", "khankir pola", 
    "pola", "chudani", "shala", "shali", "bailla", "choocha", "choddu", "guu", 
    "gu", "haggu", "mutki", "baba", "mai", "bap", "shokhi", "shon", "shala",
    "baler bacha", "magir pola", "khankir magi", "bhencho", "madar", "chudir bhai",
    "guer bacha", "hagur pola", "tui chuda", "tor baap", "tor ma", "tor bon",
    "tor bou", "shalar puta", "haramzadar", "kuttar polapain", "suor", "suorer bacha",
    "shikari", "kania", "chodna pola", "balchoda", "gudar bacha", "gudmara", 
    "gudmarani", "chudani pola", "baler bhai", "fokirni", "fokirer bacha", "chocha",
    "chodon", "chudku", "chudku bacha", "ponti", "pontir pola", "bhari", "boka",
    "chotoalok", "chotoaloker bacha", "tor goy", "tor guu", "tor mukhe guu",
    "magir po", "khankir po", "chudir po", "baler po", "haramir po", "kuttar po",
    "chud-chudi", "chuda-chudi", "marani", "maranir po", "putir po", "shalar po",
    "bhenchodar", "gandugiri", "gandubaz", "hijrar bacha", "napunker bacha",
    "chudki", "chudni", "chudail", "shurkhor", "sudkhor", "chor", "dakat",
    "badmaish", "badmaisher bacha", "shoytan", "shoytaner bacha", "gonda",
    "gondar bacha", "mastan", "mastaner bacha", "lancha", "lanchar bacha",
    "kanja", "kanjar bacha", "chota", "chotar bacha", "chotamota", "faltu",
    "faltur bacha", "bekol", "pagol", "pagoler bacha", "bodmaish", "bodmaishi"
]

# মেসেজ হ্যান্ডলার
@bot.message_handler(func=lambda message: True)
def reply_to_user(message):
    if not message.text:
        return
        
    user_text = message.text.lower()
    chat_type = message.chat.type 
    
    # ১. গ্রুপ মডারেশন ও অটো-ব্যান
    if chat_type in ['group', 'supergroup']:
        if any(word in user_text for word in bad_words):
            try:
                user_name = message.from_user.first_name
                bot.delete_message(message.chat.id, message.message_id)
                bot.ban_chat_member(message.chat.id, message.from_user.id)
                
                mention = f"@{message.from_user.username}" if message.from_user.username else user_name
                bot.send_message(
                    message.chat.id, 
                    f"⚠️ {mention} আপনার বাজে আচরণের জন্য আপনাকে গ্রুপ থেকে ব্যান করা হলো!"
                )
                return
            except Exception as e:
                print(f"Ban Error: {e}")

    # ২. ভিডিও ডাউনলোডার ফিচার
    if "http://" in user_text or "https://" in user_text:
        if "youtube.com" in user_text or "youtu.be" in user_text or "facebook.com" in user_text or "instagram.com" in user_text:
            processing_msg = bot.reply_to(message, "⏳ ভিডিও ডাউনলোড হচ্ছে, একটু অপেক্ষা করো...")
            
            output_template = "video.mp4"
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': output_template,
                'max_filesize': 50 * 1024 * 1024, 
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([message.text])
                
                with open(output_template, 'rb') as vid:
                    bot.send_video(message.chat.id, vid, reply_to_message_id=message.id)
                
                bot.delete_message(message.chat.id, processing_msg.message_id)
                
                if os.path.exists(output_template):
                    os.remove(output_template)
                    
            except Exception as e:
                bot.edit_message_text(f"❌ ভিডিওটি ডাউনলোড করা সম্ভব হয়নি! (ফাইল বড় বা লিংক ভুল)", message.chat.id, processing_msg.message_id)
                print(f"Download Error: {e}")
            return

    # ৩. DuckDuckGo সার্চ ফিচার
    if user_text.startswith("search ") or user_text.startswith("google "):
        query = message.text.replace("search", "").replace("google", "").strip()
        
        searching_msg = bot.reply_to(message, f"🔍 '{query}' সম্পর্কে ইন্টারনেট থেকে তথ্য খোঁজা হচ্ছে...")
        
        try:
            results = []
            # DDGS লাইব্রেরির মাধ্যমে সার্চ করা
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=3):
                    results.append(r)
            
            if results:
                response_text = f"🌐 **সার্চ ফলাফল ({query}):**\n\n"
                for i, res in enumerate(results, 1):
                    title = res.get('title', 'Link')
                    href = res.get('href', '#')
                    body = res.get('body', '')
                    response_text += f"{i}. **[{title}]({href})**\n_{body[:100]}...\n\n"
                
                bot.edit_message_text(response_text, message.chat.id, searching_msg.message_id, parse_mode="Markdown", disable_web_page_preview=True)
            else:
                bot.edit_message_text(f"❌ '{query}' সম্পর্কে কোনো ফলাফল পাওয়া যায়নি!", message.chat.id, searching_msg.message_id)
                
        except Exception as e:
            bot.edit_message_text("❌ সার্চ করতে গিয়ে সমস্যা হয়েছে!", message.chat.id, searching_msg.message_id)
            print(f"Search Error: {e}")
        return

    # ৪. সাধারণ কথার উত্তর
    if any(word in user_text for word in ["hi", "hello", "hlw", "হাই", "হ্যালো"]):
        bot.reply_to(message, "হ্যালো! কেমন আছো? বলো কীভাবে সাহায্য করতে পারি? ☺️")
        
    elif any(word in user_text for word in ["basa koi", "basa kothay", "বাসা কোথায়", "কোথায় থাকো", "basa"]):
        bot.reply_to(message, "আমি তো একটা বট! আমার বাসা ইন্টারনেটের Render সার্ভারে। ☁️📱")
        
    elif any(word in user_text for word in ["help lagbe", "sahajjo lagbe", "সাহায্য লাগবে", "হেল্প"]):
        bot.reply_to(message, "বলো তোমার কী দরকার? আমি সাহায্য করার জন্যই প্রস্তুত আছি! 🤝")
        
    else:
        if chat_type == 'private':
            bot.reply_to(message, "দুঃখিত, এই কথার উত্তর আমার সিস্টেমে নেই। তুমি চাইলে মেসেজের শুরুতে `search` লিখে যেকোনো বিষয় সার্চ করে দেখতে পারো! 🔍")

# সার্ভার ও বট রান করা
if __name__ == '__main__':
    t = threading.Thread(target=run_web)
    t.start()
    
    print("Bot is starting polling...")
    bot.infinity_polling()
