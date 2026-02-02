import telebot
from telebot import types
import json
import os

# --- আপনার তথ্য বসান ---
API_TOKEN = '8379651872:AAEZcbenCPXjGM7lbxgv0037u68JM4btR2k'
ADMIN_ID = 5857683487  # <--- @userinfobot থেকে পাওয়া আপনার আইডি এখানে দিন
ADMIN_USERNAME = "@FSBD_ADMIN_2"  # <--- আপনার ইউজারনেম দিন
BKASH_NUMBER = "01310989466"

bot = telebot.TeleBot(API_TOKEN)
DATA_FILE = "matches.json"

# --- ম্যাচ ডাটা লোড এবং সেভ করার ফাংশন ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# শুরুতে ডাটা লোড করা
MATCHES = load_data()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('📅 ম্যাচ শিডিউল')
    btn2 = types.KeyboardButton('🎮 টুর্নামেন্টে যোগ দিন')
    btn3 = types.KeyboardButton('💰 টাকা উত্তোলন (Withdraw)')
    btn4 = types.KeyboardButton('📞 সাপোর্ট (Support)')
    markup.add(btn1, btn2, btn3, btn4)
    
    welcome_text = "স্বাগতম! Free Fire Tournament বটের মেইন মেনু।"
    if message.from_user.id == ADMIN_ID:
        welcome_text += "\n\n🛠 *অ্যাডমিন প্যানেল:*\nম্যাচ যোগ: /add \nম্যাচ মুছতে: /remove"
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# --- ১. সাপোর্ট বাটন ---
@bot.message_handler(func=lambda message: message.text == '📞 সাপোর্ট (Support)')
def support_info(message):
    markup = types.InlineKeyboardMarkup()
    support_link = types.InlineKeyboardButton("💬 ম্যানেজারের সাথে কথা বলুন", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")
    markup.add(support_link)
    bot.send_message(message.chat.id, "যেকোনো সমস্যায় আমাদের সাথে সরাসরি যোগাযোগ করুন।", reply_markup=markup)

# --- ২. অ্যাডমিন প্যানেল: ম্যাচ যোগ করা ---
@bot.message_handler(commands=['add'])
def add_match_command(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.send_message(message.chat.id, "ম্যাচের নাম এবং টাকা এভাবে লিখুন:\n`সলো-৫০ টাকা` (মাঝখানে একটি হাইফেন দিন)")
        bot.register_next_step_handler(msg, process_add_match)

def process_add_match(message):
    global MATCHES
    try:
        if '-' in message.text:
            name, fee = message.text.split('-')
            match_id = f"match_{len(MATCHES) + 1}"
            MATCHES[match_id] = {"name": name.strip(), "fee": fee.strip()}
            save_data(MATCHES) # ফাইলে সেভ করা
            bot.send_message(message.chat.id, f"✅ সফল! '{name.strip()}' ম্যাচটি সেভ হয়েছে।")
        else:
            bot.send_message(message.chat.id, "❌ ফরম্যাট ভুল! (উদাহরণ: সলো-৫০ টাকা)")
    except:
        bot.send_message(message.chat.id, "এরর হয়েছে। আবার চেষ্টা করুন।")

# --- ৩. অ্যাডমিন প্যানেল: ম্যাচ মোছা ---
@bot.message_handler(commands=['remove'])
def remove_match_command(message):
    if message.from_user.id == ADMIN_ID:
        if not MATCHES:
            bot.send_message(message.chat.id, "বর্তমানে কোনো ম্যাচ নেই।")
            return
        
        markup = types.InlineKeyboardMarkup()
        for m_id, m_info in MATCHES.items():
            markup.add(types.InlineKeyboardButton(f"❌ {m_info['name']}", callback_data=f"del_{m_id}"))
        bot.send_message(message.chat.id, "কোন ম্যাচটি মুছতে চান?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('del_'))
def delete_match(call):
    global MATCHES
    m_id = call.data.replace('del_', '')
    if m_id in MATCHES:
        del MATCHES[m_id]
        save_data(MATCHES) # ফাইল থেকে আপডেট করা
        bot.answer_callback_query(call.id, "ম্যাচটি মুছে ফেলা হয়েছে।")
        bot.edit_message_text("✅ ম্যাচটি ডিলিট করা হয়েছে এবং মেমোরি থেকে মুছে গেছে।", call.message.chat.id, call.message.message_id)

# --- ৪. ইউজার প্যানেল: টুর্নামেন্টে যোগ দেওয়া ---
@bot.message_handler(func=lambda message: message.text == '🎮 টুর্নামেন্টে যোগ দিন')
def show_matches(message):
    if not MATCHES:
        bot.send_message(message.chat.id, "বর্তমানে কোনো সক্রিয় ম্যাচ নেই।")
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    for m_id, m_info in MATCHES.items():
        btn = types.InlineKeyboardButton(f"{m_info['name']} - {m_info['fee']}", callback_data=f"join_{m_id}")
        markup.add(btn)
    bot.send_message(message.chat.id, "কোন ম্যাচে জয়েন হতে চান?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('join_'))
def handle_join(call):
    m_id = call.data.replace('join_', '')
    if m_id in MATCHES:
        selected_match = MATCHES[m_id]
        msg = bot.send_message(call.message.chat.id, f"আপনি নির্বাচন করেছেন: {selected_match['name']}\n\nআপনার *গেমের নাম ও UID* লিখে পাঠান:")
        bot.register_next_step_handler(msg, ask_payment, selected_match)

def ask_payment(message, selected_match):
    user_info = message.text
    pay_msg = (f"✅ তথ্য পাওয়া গেছে।\n\n"
               f"📌 *পেমেন্ট তথ্য:*\n"
               f"এন্ট্রি ফি: {selected_match['fee']}\n"
               f"বিকাশ নম্বর: {BKASH_NUMBER}\n\n"
               f"টাকা পাঠিয়ে আপনার *TrxID* লিখে মেসেজ দিন।")
    bot.send_message(message.chat.id, pay_msg, parse_mode="Markdown")
    bot.register_next_step_handler(message, final_step, selected_match, user_info)

def final_step(message, selected_match, user_info):
    bot.send_message(message.chat.id, "✅ আবেদন সফল! ম্যানেজার চেক করে আপনাকে জানিয়ে দিবে।")
    admin_log = (f"🔔 *নতুন রেজিস্ট্রেশন!*\n\n👤 নাম: {message.from_user.first_name}\n🎮 ম্যাচ: {selected_match['name']}\n📝 তথ্য: {user_info}\n💳 TrxID: {message.text}")
    bot.send_message(ADMIN_ID, admin_log)

# --- ৫. টাকা উত্তোলন (Withdraw) ---
@bot.message_handler(func=lambda message: message.text == '💰 টাকা উত্তোলন (Withdraw)')
def withdraw(message):
    msg = bot.send_message(message.chat.id, "আপনার বিকাশ নম্বর দিন:")
    bot.register_next_step_handler(msg, process_withdraw)

def process_withdraw(message):
    bot.send_message(message.chat.id, "✅ আবেদন সফল!")
    bot.send_message(ADMIN_ID, f"💸 *উইথড্র রিকোয়েস্ট!*\nইউজার: {message.from_user.first_name}\nনম্বর: {message.text}")

# --- ৬. শিডিউল ---
@bot.message_handler(func=lambda message: message.text == '📅 ম্যাচ শিডিউল')
def schedule(message):
    if not MATCHES:
        bot.send_message(message.chat.id, "বর্তমানে কোনো ম্যাচ নেই।")
        return
    text = "📋 *বর্তমান শিডিউল:*\n\n"
    for m in MATCHES.values():
        text += f"🔹 {m['name']} - ফি: {m['fee']}\n"
    bot.send_message(message.chat.id, text)

print("বট সচল আছে (পারমানেন্ট ডাটা স্টোরেজ সহ)...")
bot.infinity_polling()
