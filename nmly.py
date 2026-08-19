import os
import re
import json
import uuid
import requests
import nest_asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ChatMemberHandler, filters, ContextTypes
import yt_dlp

# تفعيل بيئة كولاب
nest_asyncio.apply()

# ================= الإعدادات الأساسية =================
TOKEN = "6554337377:AAHas3gWBVM8WI0Cvzl68S-9-XYbC2oZvC8" # توكن بوتك
DEVELOPER_ID = 5543325412 # الايدي الخاص بك
TIKTOK_API = "https://tikwm.com/api/"
DATA_FILE = "bot_data.json"
# ======================================================

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": [], "groups": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in db["users"]:
        db["users"].append(user_id)
        save_data(db)
        
    # رسالة الترحيب مع الرمز المتحرك
    msg = (
        "مرحباً بك في بوت التحميل التابع لبوت ماريا <tg-emoji emoji-id=\"5382210049047275301\">✨</tg-emoji>\n\n"
        "<tg-emoji emoji-id=\"5458491661816438023\">✨</tg-emoji>  قناة التحديثات <tg-emoji emoji-id=\"5346230992044574063\">✨</tg-emoji> @suooc\n\n"
        "<tg-emoji emoji-id=\"6028443090535059075\">✨</tg-emoji>  أرسل رابط المقطع الي تبيه من التيك أو الانستا عشان احمله لك يحب"
    )
    await update.message.reply_text(msg, parse_mode='HTML')

def fetch_tiktok_data(url: str):
    try:
        response = requests.post(TIKTOK_API, data={"url": url, "count": 12, "cursor": 0, "web": 1, "hd": 1})
        data = response.json()
        if data.get("code") == 0:
            return data.get("data")
        return None
    except Exception as e:
        print("TikTok API Error:", e)
        return None

async def track_bot_joins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    chat = result.chat
    new_status = result.new_chat_member.status
    old_status = result.old_chat_member.status
    
    if new_status in ["member", "administrator"] and old_status not in ["member", "administrator"]:
        if str(chat.id) not in db["groups"]:
            db["groups"].append(str(chat.id))
            save_data(db)
            
        link = "الرابط غير متوفر (البوت ليس مشرف)"
        if new_status == "administrator":
            try: link = await context.bot.export_chat_invite_link(chat.id)
            except Exception: pass
                
        msg = f"تمت إضافة البوت لقروب جديد.\n\n- الاسم: {chat.title}\n- الايدي: {chat.id}\n- الرابط: {link}\n\n- عدد القروبات الكلي الآن: {len(db['groups'])}"
        await context.bot.send_message(chat_id=DEVELOPER_ID, text=msg)
        
    elif new_status in ["left", "kicked", "banned"] and old_status in ["member", "administrator"]:
        if str(chat.id) in db["groups"]:
            db["groups"].remove(str(chat.id))
            save_data(db)
            
        msg = f"تم طرد البوت أو خروجه من قروب.\n\n- الاسم: {chat.title}\n- الايدي: {chat.id}\n\n- عدد القروبات الكلي الآن: {len(db['groups'])}"
        await context.bot.send_message(chat_id=DEVELOPER_ID, text=msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    user_id = str(update.message.from_user.id)
    chat_id = str(update.message.chat_id)
    chat_type = update.message.chat.type
    
    if user_id not in db["users"]:
        db["users"].append(user_id)
        save_data(db)
    if chat_type in ['group', 'supergroup'] and chat_id not in db["groups"]:
        db["groups"].append(chat_id)
        save_data(db)

    if text in ["الاحصائيات", "إحصائيات"]:
        if int(user_id) == DEVELOPER_ID:
            stats_msg = f"إحصائيات البوت الحالية:\n\n- عدد المستخدمين: {len(db['users'])}\n- عدد القروبات: {len(db['groups'])}"
            return await update.message.reply_text(stats_msg)
        else:
            return

    url_match = re.search(r'(https?://[^\s]+)', text)
    if not url_match:
        if text in ["تيك", "تيك توك", "انستا", "انستقرام"]:
            return await update.message.reply_text("أرسل رابط المقطع الي تبيه عشان احمله لك يحب")
        return

    target_url = url_match.group(1)

    # ================= قسم الانستقرام =================
    if "instagram.com" in target_url:
        status_msg = await update.message.reply_text("ابشر الان احمله لك ياقلبي")
        
        clean_url = target_url.split("?")[0]
        file_name = f"insta_{uuid.uuid4().hex}.mp4"
        
        try:
            ydl_opts = {
                'outtmpl': file_name,
                'quiet': True,
                'no_warnings': True,
                'format': 'best'
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clean_url, download=True)
                
            if os.path.exists(file_name):
                title = info.get('description') or info.get('title') or "بدون وصف"
                if len(title) > 100: title = title[:100] + "..."
                
                author = info.get('uploader') or info.get('channel') or "غير معروف"

                # الوصف مع الرمز المتحرك
                caption = (
                    f"<tg-emoji emoji-id=\"5116113383128564448\">✨</tg-emoji>  الاسم  <tg-emoji emoji-id=\"5346230992044574063\">✨</tg-emoji>  {author}\n"
                    f"<tg-emoji emoji-id=\"5116113383128564448\">✨</tg-emoji>  الوصف  <tg-emoji emoji-id=\"5346230992044574063\">✨</tg-emoji>  {title}"
                )
                
                # --- كود زر تحميل الصوت للانستا ---
                ig_id = info.get('id', uuid.uuid4().hex[:8])
                context.bot_data[f"igaudio_{ig_id}"] = clean_url
                keyboard = [[InlineKeyboardButton("تحميل الصوت", callback_data=f"igaudio_{ig_id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                # ----------------------------------

                await update.message.reply_video(
                    video=open(file_name, 'rb'),
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=reply_markup,
                    reply_to_message_id=update.message.message_id
                )
                await status_msg.delete()
                os.remove(file_name)
            else:
                await status_msg.edit_text("عذرا، فشل التحميل. تأكد أن الحساب عام أو أن الرابط صحيح.")
                
        except Exception as e:
            print("Insta Download Error:", e)
            await status_msg.edit_text("حدث خطأ أثناء تحميل المقطع، تأكد أن الحساب عام وليس خاصا.")
            if os.path.exists(file_name): os.remove(file_name)
        return

    # ================= قسم التيك توك =================
    elif "tiktok.com" in target_url:
        status_msg = await update.message.reply_text("ابشر الان احمله لك ياقلبي")
        data = fetch_tiktok_data(target_url)

        if not data:
            return await status_msg.edit_text("عذرا، فشل جلب الفيديو. تأكد أن الحساب ليس خاصا أو جرب رابطا آخر.")

        video_url = data.get("play")
        music_url = data.get("music")
        
        if video_url and not video_url.startswith("http"): video_url = "https://www.tikwm.com" + video_url
        if music_url and not music_url.startswith("http"): music_url = "https://www.tikwm.com" + music_url

        video_id = data.get("id")
        title = data.get("title", "بدون عنوان")
        author = data.get("author", {}).get("nickname", "غير معروف")

        # الوصف مع الرمز المتحرك
        caption = (
            f"<tg-emoji emoji-id=\"5116113383128564448\">✨</tg-emoji>  الاسم  <tg-emoji emoji-id=\"5346230992044574063\">✨</tg-emoji>  {author}\n"
            f"<tg-emoji emoji-id=\"5116113383128564448\">✨</tg-emoji>  الوصف  <tg-emoji emoji-id=\"5346230992044574063\">✨</tg-emoji>  {title}"
        )

        keyboard = []
        if music_url:
            context.bot_data[f"tkaudio_{video_id}"] = music_url
            keyboard.append([InlineKeyboardButton("تحميل الصوت", callback_data=f"tkaudio_{video_id}")])

        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

        try:
            await update.message.reply_video(
                video=video_url,
                caption=caption,
                parse_mode='HTML', 
                reply_markup=reply_markup,
                reply_to_message_id=update.message.message_id
            )
            await status_msg.delete()
        except Exception as e:
            print("TikTok Send Error:", e)
            await status_msg.edit_text("حدث خطأ أثناء إرسال الفيديو، قد يكون حجمه كبيرا جدا.")
        return

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("الان احملك الصوت يحب")
    
    # ================= قسم استخراج الصوت للانستقرام =================
    if query.data.startswith("igaudio_"):
        ig_url = context.bot_data.get(query.data)
        if not ig_url:
            return await query.message.reply_text("عذرا، انتهت صلاحية هذا الرابط. أرسل المقطع مرة أخرى.")
            
        base_name = f"audio_{uuid.uuid4().hex}"
        final_audio = f"{base_name}.mp3"
        try:
            ydl_opts = {
                'outtmpl': f'{base_name}.%(ext)s',
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([ig_url])
                
            await query.message.reply_audio(
                audio=open(final_audio, 'rb'),
                caption="جبت لك الصوتيه ياروحي",
                title="هذا صوت المقطع",      # تغيير اسم المقطع من الداخل
                filename="هذا صوت المقطع.mp3", # تغيير اسم الملف
                reply_to_message_id=query.message.message_id
            )
            os.remove(final_audio)
        except Exception as e:
            print("IG Audio Error:", e)
            await query.message.reply_text("حدث خطأ أثناء استخراج الصوت من الانستا.")
            if os.path.exists(final_audio): os.remove(final_audio)
        return

    # ================= قسم استخراج الصوت للتيك توك =================
    # ================= قسم استخراج الصوت للتيك توك =================
    elif query.data.startswith("tkaudio_"):
        music_url = context.bot_data.get(query.data)
        if not music_url:
            return await query.message.reply_text("عذرا، انتهت صلاحية هذا الصوت. أرسل الرابط مرة أخرى.")

        try:
            # تحميل الصوت محلياً عشان نجبر تليجرام يغير اسمه
            audio_req = requests.get(music_url)
            tk_audio_name = f"tk_{uuid.uuid4().hex}.mp3"
            
            with open(tk_audio_name, 'wb') as f:
                f.write(audio_req.content)

            await query.message.reply_audio(
                audio=open(tk_audio_name, 'rb'),
                caption="جبت لك الصوتيه ياروحي",
                title="هذا صوت المقطع",      # تغيير اسم المقطع من الداخل
                filename="هذا صوت المقطع.mp3", # تغيير اسم الملف الخارجي
                reply_to_message_id=query.message.message_id
            )
            os.remove(tk_audio_name)
        except Exception as e:
            print("Send Audio Error:", e)
            await query.message.reply_text("حدث خطأ أثناء تحميل الصوت.")
            if os.path.exists(tk_audio_name): os.remove(tk_audio_name)

# ================= تشغيل البوت =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(ChatMemberHandler(track_bot_joins, ChatMemberHandler.MY_CHAT_MEMBER))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(handle_callback))

print("تم تشغيل البوت بنجاح لدعم تيك توك وإنستقرام 🚀")
app.run_polling()
