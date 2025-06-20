import json
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from datetime import datetime

TOKEN = '8146754055:AAGGtB5yLNWnRn17rXtJi1dbCb5Fvf-DU70'

DATA_FILE = "userdata.json"
user_data = {}

def load_data():
    global user_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            user_data = json.load(f)

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)

def start(update, context):
    update.message.reply_text("Бот активен!")

def warn(update, context):
    if not update.message.reply_to_message:
        update.message.reply_text("Ответь на сообщение пользователя для предупреждения.")
        return

    # Получаем ID пользователя, который вызвал команду
    admin_id = update.effective_user.id

    # Получаем список администраторов чата
    chat_admins = [admin.user.id for admin in context.bot.get_chat_administrators(update.message.chat_id)]

    # Проверка: является ли пользователь администратором
    if admin_id not in chat_admins:
        update.message.reply_text("Только администраторы могут выдавать предупреждения.")
        return

    # Продолжаем если пользователь — админ
    user = update.message.reply_to_message.from_user
    user_id = str(user.id)

    if user_id not in user_data:
        user_data[user_id] = {
            "nickname": user.first_name,
            "warns": 1,
            "roles": [],
            "joined": str(datetime.now())
        }
    else:
        user_data[user_id]["warns"] = user_data[user_id].get("warns", 0) + 1

    warns = user_data[user_id]["warns"]
    save_data()

    if warns >= 6:
        try:
            update.message.chat.kick_member(user.id)
            update.message.reply_text(f"{user.first_name} получил 6/6 предупреждений и был забанен.")
        except:
            update.message.reply_text("Не удалось забанить пользователя.")
    else:
        update.message.reply_text(f"{user.first_name} получил предупреждение {warns}/6.")

def unwarn(update: Update, context: CallbackContext):
    if not update.message.reply_to_message:
        update.message.reply_text("Ответь на сообщение пользователя, чтобы снять варн.")
        return

    admin_id = update.effective_user.id
    chat_admins = [admin.user.id for admin in context.bot.get_chat_administrators(update.message.chat_id)]
    
    if admin_id not in chat_admins:
        update.message.reply_text("Только администраторы могут снимать предупреждения.")
        return

    user_id = str(update.message.reply_to_message.from_user.id)
    user_entry = user_data.get(user_id, {})
    warns = user_entry.get("warns", 0)

    if warns > 0:
        user_entry["warns"] = warns - 1
        user_data[user_id] = user_entry
        save_data()
        update.message.reply_text(f"С пользователя снят 1 варн. Теперь варнов: {user_entry['warns']}/6.")
    else:
        update.message.reply_text("У пользователя нет варнов.")
        
def kick(update: Update, context: CallbackContext):
    if not update.message.reply_to_message:
        update.message.reply_text("Ответь на сообщение, чтобы кикнуть пользователя.")
        return

    # Проверка, является ли вызывающий пользователь админом
    admin_id = update.effective_user.id
    chat_admins = [admin.user.id for admin in context.bot.get_chat_administrators(update.message.chat_id)]

    if admin_id not in chat_admins:
        update.message.reply_text("Только администраторы могут использовать эту команду.")
        return

    # Кикаем пользователя
    try:
        user_to_kick = update.message.reply_to_message.from_user
        update.message.chat.kick_member(user_to_kick.id)
        update.message.reply_text(f"{user_to_kick.first_name} был кикнут.")
    except:
        update.message.reply_text("Не удалось исключить пользователя.")
                                  
def ban(update: Update, context: CallbackContext):
    if not update.message.reply_to_message:
        update.message.reply_text("Ответь на сообщение, чтобы забанить пользователя.")
        return

    # Проверка, является ли вызывающий команду админом
    admin_id = update.effective_user.id
    chat_admins = [admin.user.id for admin in context.bot.get_chat_administrators(update.message.chat_id)]

    if admin_id not in chat_admins:
        update.message.reply_text("Только администраторы могут использовать эту команду.")
        return

    # Блокировка пользователя
    try:
        user_to_ban = update.message.reply_to_message.from_user
        update.message.chat.kick_member(user_to_ban.id)
        update.message.reply_text(f"{user_to_ban.first_name} был забанен.")
    except:
        update.message.reply_text("Не удалось забанить пользователя.")
        
def unban(update: Update, context: CallbackContext):
    admin_id = update.effective_user.id
    chat_admins = [admin.user.id for admin in context.bot.get_chat_administrators(update.message.chat_id)]

    if admin_id not in chat_admins:
        update.message.reply_text("Только администраторы могут использовать эту команду.")
        return

    try:
        user_id = int(context.args[0])
        update.message.chat.unban_member(user_id)
        update.message.reply_text("Пользователь разбанен.")
    except (IndexError, ValueError):
        update.message.reply_text("Укажи ID пользователя: .разбан <id>")
    except Exception as e:
        update.message.reply_text(f"Ошибка при разбане: {e}")
        
def set_name(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = str(user.id)

    nickname = update.message.text.split(maxsplit=1)
    if len(nickname) < 2:
        update.message.reply_text("Укажи ник: .имя <твой_ник>")
        return

    nickname_text = nickname[1]  

    if user_id not in user_data:
        user_data[user_id] = {"nickname": nickname_text, "warns": 0, "roles": [], "joined": str(datetime.now())}
    else:
        user_data[user_id]["nickname"] = nickname_text

    save_data()
    update.message.reply_text(f"Твой ник изменён на: {nickname_text}")
def we_command(update: Update, context: CallbackContext):
    update.message.reply_text("𝑼𝒏𝒅𝒆𝒓 𝒕𝒉𝒆 𝒎𝒐𝒐𝒏𝒍𝒊𝒈𝒉𝒕 🌑")
    
def show_nick(update, context):
    user_id = str(update.effective_user.id)
    nickname = user_data.get(user_id, {}).get("nickname", update.effective_user.first_name)
    update.message.reply_text(f" 𝓾𝓽𝓶 || {nickname} ⇣  🌑 ")

def give_role(update: Update, context: CallbackContext):
    if not update.message.reply_to_message or not context.args:
        update.message.reply_text("Использование: .роль <роль> (в ответ на сообщение)")
        return

    admin_id = update.effective_user.id
    chat_admins = [admin.user.id for admin in context.bot.get_chat_administrators(update.message.chat_id)]

    if admin_id not in chat_admins:
        update.message.reply_text("Только администраторы могут выдавать роли.")
        return

    role = ' '.join(context.args)
    user = update.message.reply_to_message.from_user
    user_id = str(user.id)

    if user_id not in user_data:
        user_data[user_id] = {"nickname": user.first_name, "warns": 0, "roles": [], "joined": str(datetime.now())}

    if role not in user_data[user_id]["roles"]:
        user_data[user_id]["roles"].append(role)
        save_data()
        update.message.reply_text(f"Роль '{role}' выдана {user.first_name}.")
    else:
        update.message.reply_text(f"У {user.first_name} уже есть эта роль.")

def remove_role(update, context):
    if not update.message.reply_to_message or not context.args:
        update.message.reply_text("Использование: /removerole <роль> (в ответ на сообщение)")
        return
    admin = update.effective_user
    chat_admins = [admin.user.id for admin in context.bot.get_chat_administrators(update.message.chat_id)]
    if admin.id not in chat_admins:
        update.message.reply_text("Только администраторы могут удалять роли.")
        return
    role = ' '.join(context.args)
    user = update.message.reply_to_message.from_user
    user_id = str(user.id)
    if user_id in user_data and role in user_data[user_id]["roles"]:
        user_data[user_id]["roles"].remove(role)
        update.message.reply_text(f"Роль '{role}' удалена у {user.first_name}.")
        save_data()
    else:
        update.message.reply_text("Роль не найдена у пользователя.")

def welcome_new_member(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        username = f"@{member.username}" if member.username else member.full_name

        text = f"""
🌘 𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝒕𝒐 𝒕𝒉𝒆 𝒔𝒊𝒍𝒆𝒏𝒕 𝒔𝒊𝒅𝒆... 🌒  
пρᥙʙᥱᴛᥴᴛʙуᥱʍ ᴛᥱδя, {username}!

Ты ᴛ᧐᧘ьκ᧐ чᴛ᧐ ᧐ᴛκρы᧘ дʙᥱρь ʙ ʍᥙρ, ᴦдᥱ κᥲждыᥔ х᧐д — ϶ᴛ᧐ ᧐ᴛρᥲжᥱнᥙᥱ ʙ ᧘унн᧐ᥔ ʙ᧐дᥱ - ʙ нᥲɯᥱʍ ᴛёʍн᧐ʍ ᥙ κρᥲᥴᥙʙ᧐ʍ ᥰρ᧐ᥴᴛρᥲнᥴᴛʙᥱ

            ❝ 𝑼𝒏𝒅𝒆𝒓 𝒕𝒉𝒆 𝒎𝒐𝒐𝒏𝒍𝒊𝒈𝒉𝒕 ❞

━━━━━━━━━━━━━━━

╭ ⊹ ꒰ Вᥴя ᥰ᧐᧘ᥱɜнᥲя ᥙнɸ᧐ρʍᥲцᥙя д᧘я н᧐ʙᥙчκ᧐ʙ — нᥙжᥱ.
╰ ⊹  Зᥲдᥲʙᥲᥔ ʙ᧐ᥰρ᧐ʴы, нᥱ δ᧐ᥔᥴя учᥲᥴᴛʙ᧐ʙᥲᴛь ᥙ ᥴᥙяᥔ ʙ нᥲɯᥙх ᥙᴦρᥲх.

Д᧐ ʙᥴᴛρᥱчᥙ нᥲ ᥲρᥱнᥱ, 𝒍𝒖𝒏𝒂𝒓 𝒈𝒖𝒆𝒔𝒕. 🌙
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Information", url="https://t.me/+m7fO4Q3Xx2diMjAy")],
            [InlineKeyboardButton("🧭 Guide", url="https://t.me/+R3it2sniWV1jZGEy")],
            [InlineKeyboardButton("🗞 News", url="https://t.me/+uJh7MjVloBYyY2Yy")]
        ])
        update.message.reply_text(text, reply_markup=keyboard)

def goodbye(update: Update, context: CallbackContext): 
    user = update.message.left_chat_member
    name = user.first_name
    text = f"""
{name} покидает наш путь под лунным светом. Каждый оставляет след, и твой останется в истории Under the Moonlight 🌒. Спасибо за игру, за участие и за то, что был(а) частью нашей ночной легенды.

𝒏𝒐𝒘… 𝒕𝒉𝒆 𝒎𝒐𝒐𝒏 𝒔𝒉𝒊𝒏𝒆𝒔 𝒇𝒐𝒓 𝒂𝒏𝒐𝒕𝒉𝒆𝒓.

Желаем удачи — где бы ты ни оказался(ась) 🌙
"""
    update.message.reply_text(text)

def send_cc_link(update: Update, context: CallbackContext):
    update.message.reply_text("https://t.me/+dWD8UqTCjGE4YWQ6")
    
def info(update, context):
    if not update.message.reply_to_message:
        update.message.reply_text("Ответь на сообщение пользователя для инфо.")
        return
    user = update.message.reply_to_message.from_user
    user_id = str(user.id)
    data = user_data.get(user_id, {})
    nickname = data.get("nickname", user.first_name)
    warns = data.get("warns", 0)
    username = f"@{user.username}" if user.username else "Не указано"
    joined = data.get("joined", "Неизвестно")
    roles = data.get("roles", [])
    roles_text = "\n".join([f" ├ {r}" for r in roles]) if roles else " └ Нет ролей"

    text = (
        f"🆔 ID: {user.id} #id{user.id}\n"
        f"👱 Имя: {nickname} (!)\n"
        f"🌐 Имя пользователя: {username}\n"
        f"👀 Состояние: В группе\n"
        f"➰ Роли:\n{roles_text}\n"
        f"❕ Предупреждения: {warns}/6\n"
        f"⤵️ Вступил(а): {joined}\n"
        f"🇷🇺 Язык: Russian"
    )
    update.message.reply_text(text)

def main():
    load_data()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'^\.старт$'), start))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'^\.варн$'), warn))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'^\.кик$'), kick))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'^\.бан$'), ban))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'^\.разбан\b'), unban))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'^\.имя\b'), set_name))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'^\.инфо$'), info))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'^\.ник$'), show_nick))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'^\.роль\b'), give_role))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'^\.удалитьроль\b'), remove_role))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r"^\.unwarn$"), unwarn))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'^\.мы$'), we_command))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome_new_member))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, goodbye))
    dp.add_handler(MessageHandler(Filters.text & Filters.regex(r'^\.cc$'), send_cc_link))

    updater.start_polling()
    print("Бот запущен!")
    updater.idle()

if __name__ == '__main__':
    main()
