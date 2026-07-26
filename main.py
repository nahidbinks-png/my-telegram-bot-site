import os
import telebot
from flask import Flask
import threading
import yt_dlp
from googlesearch import search  # গুগল সার্চের জন্য নতুন লাইব্রেরি

# রেন্ডারের এনভায়রনমেন্ট থেকে টোকেন নেওয়া হচ্ছে (গিটহাভে আর সিক্রেট দেখাবে না)
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# ফ্লাস্ক ওয়েব সার্ভার তৈরি (Render-এর পোর্ট ওপেন রাখার জন্য)
app = Flask('')

@app.route('/')
def home():
    return "BotSphere is online and running!"

def run_web():
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)

# গালি বা খারাপ শব্দের বিশাল তালিকা
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

# তোমার কাস্টম মেসেজ এবং মডারেশন হ্যান্ডলার ফাংশন
@bot.message_handler(func=lambda message: True)
def reply_to_user(message):
    if not message.text:
        return
        
    # ইউজার যা লিখবে সেটাকে ছোট হাতের অক্ষরে (lowercase) করে নেবে, যাতে ম্যাচ করতে সুবিধা হয়
    user_text = message.text.lower()
    chat_type = message.chat.type # চ্যাটটি গ্রুপ নাকি প্রাইভেট তা চেক করা হচ্ছে
    
    # ১. গ্রুপ বা সুপারগ্রুপের জন্য গালি ফিল্টার ও অটো-ব্যান চেক
    if chat_type in ['group', 'supergroup']:
        if any(word in user_text for word in bad_words):
            try:
                user_name = message.from_user.first_name
                
                # গালিযুক্ত মেসেজটি ডিলিট করা
                bot.delete_message(message.chat.id, message.message_id)
                
                # ইউজারকে গ্রুপ থেকে ব্যান করা
                bot.ban_chat_member(message.chat.id, message.from_user.id)
                
                # বাংলায় কারণসহ মেসেজ পাঠানো
                mention = f"@{message.from_user.username}" if message.from_user.username else user_name
                bot.send_message(
                    message.chat.id, 
                    f"⚠️ {mention} আপনার বাজে আচরণের জন্য আপনাকে গ্রুপ থেকে ব্যান করা হলো!"
                )
                return
            except Exception as e:
                print(f"Ban Error (Admin permission lagte pare): {e}")

    # ২. ভিডিও ডাউনলোডার ফিচার (ইউটিউব বা অন্যান্য লিংক চেক করা)
    if "http://" in user_text or "https://" in user_text:
        if "youtube.com" in user_text or "youtu.be" in user_text or "facebook.com" in user_text or "instagram.com" in user_text:
            processing_msg = bot.reply_to(message, "⏳ ভিডিও ডাউনলোড হচ্ছে, একটু অপেক্ষা করো...")
            
            output_template = "video.mp4"
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': output_template,
                'max_filesize': 50 * 1024 * 1024, # সার্ভার সুরক্ষার জন্য সর্বোচ্চ ৫০ মোবাইট লিমিট
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([message.text])
                
                # ভিডিও ফাইল ইউজারের কাছে পাঠানো
                with open(output_template, 'rb') as vid:
                    bot.send_video(message.chat.id, vid, reply_to_message_id=message.id)
                
                # প্রসেসিং মেসেজটি ডিলিট করে দেওয়া
                bot.delete_message(message.chat.id, processing_msg.message_id)
                
                # ডাউনলোড শেষে সার্ভার থেকে ফাইল মুছে ফেলা
                if os.path.exists(output_template):
                    os.remove(output_template)
                    
            except Exception as e:
                bot.edit_message_text(f"❌ ভিডিওটি ডাউনলোড করা সম্ভব হয়নি! (সম্ভবত ফাইলটি অনেক বড় বা লিংকটি সঠিক নয়)", message.chat.id, processing_msg.message_id)
                print(f"Download Error: {e}")
            return

    # ৩. গুগল সার্চ ফিচার (ইউজার যদি 'search' বা 'google' লিখে কিছু জানতে চায়)
    if user_text.startswith("search ") or user_text.startswith("google "):
        query = message.text.replace("search", "").replace("google", "").strip()
        
        searching_msg = bot.reply_to(message, f"🔍 '{query}' সম্পর্কে গুগল থেকে তথ্য খোঁজা হচ্ছে...")
        
        try:
            results = []
            for url in search(query, num_results=3):
                results.append(url)
            
            if results:
                response_text = f"🌐 **গুগল সার্চ ফলাফল ({query}):**\n\n"
                for i, url in enumerate(results, 1):
                    response_text += f"{i}. {url}\n"
                
                bot.edit_message_text(response_text, message.chat.id, searching_msg.message_id, parse_mode="Markdown")
            else:
                bot.edit_message_text("❌ কোনো ফলাফল পাওয়া যায়নি!", message.chat.id, searching_msg.message_id)
                
        except Exception as e:
            bot.edit_message_text("❌ সার্চ করতে গিয়ে সমস্যা হয়েছে!", message.chat.id, searching_msg.message_id)
            print(f"Search Error: {e}")
        return

    # ৪. সাধারণ কথার উত্তর (হাই/হ্যালো ইত্যাদি)
    if any(word in user_text for word in ["hi", "hello", "hlw", "হাই", "হ্যালো"]):
        bot.reply_to(message, "হ্যালো! কেমন আছো? বলো কীভাবে সাহায্য করতে পারি? ☺️")
        
    elif any(word in user_text for word in ["basa koi", "basa kothay", "basa kothey", "বাসা কোথায়", "কোথায় থাকো", "basa"]):
        bot.reply_to(message, "আমি তো একটা বট! আমার বাসা হলো ইন্টারনেটে (Render সার্ভারে), তবে আমি সবসময় তোমার ফোনেই থাকি! ☁️📱")
        
    elif any(word in user_text for word in ["kno msg", "keno message", "msg keno", "msg diso", "কেন মেসেজ"]):
        bot.reply_to(message, "তুমি আমাকে তৈরি করে চালু করেছো, তাই আমি তোমার সাথে কথা বলছি। আমি তো তোমারই বানানো! 🤖")
        
    elif any(word in user_text for word in ["help lagbe", "sahajjo lagbe", "kono help", "সাহায্য লাগবে", "হেল্প"]):
        bot.reply_to(message, "আমার কোনো সাহায্য লাগবে না, কারণ আমি তোমাকেই সাহায্য করার জন্য তৈরি হয়েছি! বলো তোমার কী দরকার? 🤝")
        
    elif any(word in user_text for word in ["amr somporko", "jante chaw", "janthe chey", "ki jante chasso", "আমার সম্পর্কে", "কী জানতে চাও"]):
        bot.reply_to(message, "তুমি আমার বস! আমি তোমার সম্পর্কে এটুকুই জানি। তুমি আমাকে যা নির্দেশ দেবে, আমি ঠিক সেটাই করবো! 🚀")
        
    else:
        # শুধুমাত্র ইনবক্সে (Private Chat) অচেনা কথার উত্তর দেবে, গ্রুপে ফালতু স্প্যাম করবে না
        if chat_type == 'private':
            bot.reply_to(message, "দুঃখিত, তোমার এই কথাটার উত্তর আমার সিস্টেমে এখনো যোগ করা হয়নি। তুমি চাইলে মেসেজের শুরুতে `search` লিখে গুগল থেকে যেকোনো তথ্য খুঁজে নিতে পারো! 🔍")

# মেইন ফাংশন যেখানে ওয়েব সার্ভার ও বট একসাথে রান হবে
if __name__ == '__main__':
    # ফ্লাস্ক সার্ভার আলাদা একটি থ্রেডে রান করানো হলো
    t = threading.Thread(target=run_web)
    t.start()
    
    # টেলিগ্রাম বট পোলিং শুরু করা হলো
    print("Bot is starting polling...")
    bot.infinity_polling()
