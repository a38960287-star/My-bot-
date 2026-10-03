import os
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ✏️ غيّر الاسم ده لاسمك أو حقوقك
OWNER = "اسمك أو حقوقك"
COPYRIGHT = f"© {OWNER} - جميع الحقوق محفوظة"

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📌 المساعدة", callback_data="help"),
        InlineKeyboardButton("👤 المطور", callback_data="dev")
    )
    markup.row(
        InlineKeyboardButton("© الحقوق", callback_data="rights")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    text = (
        f"أهلاً بك في بوت {OWNER}!\n"
        f"أنا بوتك الخاص. استخدم الأزرار بالأسفل.\n\n"
        f"{COPYRIGHT}"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.message_handler(commands=['help'])
def help_command(message):
    text = (
        "الأوامر المتاحة:\n"
        "/start - بدء البوت\n"
        "/help - المساعدة\n\n"
        f"{COPYRIGHT}"
    )
    bot.reply_to(message, text)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "help":
        bot.answer_callback_query(call.id, "تم فتح المساعدة")
        bot.send_message(call.message.chat.id, "هذه هي المساعدة. يمكنك مراسلة المطور لأي استفسار.")
    elif call.data == "dev":
        bot.answer_callback_query(call.id, "المطور")
        bot.send_message(call.message.chat.id, f"المطور: {OWNER}")
    elif call.data == "rights":
        bot.answer_callback_query(call.id, "الحقوق")
        bot.send_message(call.message.chat.id, COPYRIGHT)

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.reply_to(message, f"وصلت رسالتك: {message.text}\n\n{COPYRIGHT}")

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return '', 403

@app.route('/')
def index():
    return 'Bot is running'

@app.route('/set_webhook')
def set_webhook():
    base_url = os.environ.get('RENDER_EXTERNAL_URL') or os.environ.get('WEBHOOK_URL')
    if not base_url:
        return 'RENDER_EXTERNAL_URL or WEBHOOK_URL not set', 400
    bot.remove_webhook()
    bot.set_webhook(url=base_url + '/webhook')
    return f'Webhook set to {base_url}/webhook', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
