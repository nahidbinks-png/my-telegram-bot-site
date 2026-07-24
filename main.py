@bot.message_handler(func=lambda message: True)
def reply_to_user(message):
    # ইউজার যা লিখবে সেটাকে ছোট হাতের অক্ষরে (lowercase) করে নেবে, যাতে ম্যাচ করতে সুবিধা হয়
    user_text = message.text.lower()
    
    # ১. হাই/হ্যালো
    if any(word in user_text for word in ["hi", "hello", "hlw", "হাই", "হ্যালো"]):
        bot.reply_to(message, "হ্যালো! কেমন আছো? বলো কীভাবে সাহায্য করতে পারি? ☺️")
        
    # ২. বাসা কোথায়
    elif any(word in user_text for word in ["basa koi", "basa kothay", "basa kothey", "বাসা কোথায়", "কোথায় থাকো", "basa"]):
        bot.reply_to(message, "আমি তো একটা বট! আমার বাসা হলো ইন্টারনেটে (Render সার্ভারে), তবে আমি সবসময় তোমার ফোনেই থাকি! ☁️📱")
        
    # ৩. কেন মেসেজ দিয়েছো
    elif any(word in user_text for word in ["kno msg", "keno message", "msg keno", "msg diso", "কেন মেসেজ"]):
        bot.reply_to(message, "তুমি আমাকে তৈরি করে চালু করেছো, তাই আমি তোমার সাথে কথা বলছি। আমি তো তোমারই বানানো! 🤖")
        
    # ৪. হেল্প লাগবে কি না
    elif any(word in user_text for word in ["help lagbe", "sahajjo lagbe", "kono help", "সাহায্য লাগবে", "হেল্প"]):
        bot.reply_to(message, "আমার কোনো সাহায্য লাগবে না, কারণ আমি তোমাকেই সাহায্য করার জন্য তৈরি হয়েছি! বলো তোমার কী দরকার? 🤝")
        
    # ৫. আমার সম্পর্কে কী জানতে চাও / আমি সাহায্য করবো
    elif any(word in user_text for word in ["amr somporko", "jante chaw", "janthe chey", "ki jante chasso", "আমার সম্পর্কে", "কী জানতে চাও"]):
        bot.reply_to(message, "তুমি আমার বস! আমি তোমার সম্পর্কে এটুকুই জানি। তুমি আমাকে যা নির্দেশ দেবে, আমি ঠিক সেটাই করবো! 🚀")
        
    # বাকি সব কথার উত্তর (যদি উপরের কোনোটার সাথে না মেলে)
    else:
        bot.reply_to(message, "দুঃখিত, তোমার এই কথাটার উত্তর আমার সিস্টেমে এখনো যোগ করা হয়নি। তুমি চাইলে আমাকে নতুন কিছু শেখাতে পারো! 😅")

