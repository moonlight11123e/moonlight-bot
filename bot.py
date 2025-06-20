import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes
)

TOKEN = os.getenv("8146754055:AAGGtB5yLNWnRn17rXtJi1dbCb5Fvf-DU70")

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот активен!")

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Ответь на сообщение пользователя для предупреждения.")
    admin_id = update.effective_user.id
    chat_admins = [a.user.id for a in await context.bot.get_chat_administrators(update.effective_chat.id)]
    if admin_id not in chat_admins:
        return await update.message.reply_text("Только администраторы могут выдавать предупреждения.")
    user = update.message.reply_to_message.from_user
    uid = str(user.id)
    user_entry = user_data.setdefault(uid, {"nickname": user.first_name, "warns":0, "roles":[], "joined": str(datetime.now())})
    user_entry["warns"] += 1
    save_data()
    warns = user_entry["warns"]
    if warns >= 6:
        try:
            await context.bot.ban_chat_member(update.effective_chat.id, user.id)
            await update.message.reply_text(f"{user.first_name} получил 6/6 предупреждений и был забанен.")
        except:
            await update.message.reply_text("Не удалось забанить пользователя.")
    else:
        await update.message.reply_text(f"{user.first_name} получил предупреждение {warns}/6.")

async def unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Ответь на сообщение пользователя, чтобы снять варн.")
    admin_id = update.effective_user.id
    chat_admins = [a.user.id for a in await context.bot.get_chat_administrators(update.effective_chat.id)]
    if admin_id not in chat_admins:
        return await update.message.reply_text("Только администраторы могут снимать предупреждения.")
    uid = str(update.message.reply_to_message.from_user.id)
    entry = user_data.get(uid)
    if entry and entry.get("warns", 0) > 0:
        entry["warns"] -= 1
        save_data()
        await update.message.reply_text(f"С пользователя снят 1 варн. Теперь варнов: {entry['warns']}/6.")
    else:
        await update.message.reply_text("У пользователя нет варнов.")

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Ответь на сообщение, чтобы кикнуть пользователя.")
    admin_id = update.effective_user.id
    chat_admins = [a.user.id for a in await context.bot.get_chat_administrators(update.effective_chat.id)]
    if admin_id not in chat_admins:
        return await update.message.reply_text("Только администраторы могут использовать эту команду.")
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"{user.first_name} был кикнут.")
    except:
        await update.message.reply_text("Не удалось исключить пользователя.")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Ответь на сообщение, чтобы забанить пользователя.")
    admin_id = update.effective_user.id
    chat_admins = [a.user.id for a in await context.bot.get_chat_administrators(update.effective_chat.id)]
    if admin_id not in chat_admins:
        return await update.message.reply_text("Только администраторы могут использовать эту команду.")
    user = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(f"{user.first_name} был забанен.")
    except:
        await update.message.reply_text("Не удалось забанить пользователя.")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.effective_user.id
    chat_admins = [a.user.id for a in await context.bot.get_chat_administrators(update.effective_chat.id)]
    if admin_id not in chat_admins:
        return await update.message.reply_text("Только администраторы могут использовать эту команду.")
    try:
        uid = int(context.args[0])
        await context.bot.unban_chat_member(update.effective_chat.id, uid)
        await update.message.reply_text("Пользователь разбанен.")
    except:
        await update.message.reply_text("Укажи ID: .разбан <id>")

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await update.message.reply_text("Укажи ник: .имя <твой_ник>")
    nickname = parts[1]
    uid = str(update.effective_user.id)
    user_data.setdefault(uid, {"nickname": nickname, "warns":0, "roles":[], "joined": str(datetime.now())})
    user_data[uid]["nickname"] = nickname
    save_data()
    await update.message.reply_text(f"Твой ник изменён на: {nickname}")

async def we_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("𝑼𝒏𝒅𝒆𝒓 𝒕𝒉𝒆 𝒎𝒐𝒐𝒏𝒍𝒊𝒈𝒉𝒕 🌑")

async def show_nick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    nickname = user_data.get(uid, {}).get("nickname", update.effective_user.first_name)
    await update.message.reply_text(f" 𝓾𝓽𝓶 || {nickname} ⇣  🌑 ") 

async def give_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("Ответь на сообщение и укажи роль: .роль <роль>")
    admin_id = update.effective_user.id
    chat_admins = [a.user.id for a in await context.bot.get_chat_administrators(update.effective_chat.id)]
    if admin_id not in chat_admins:
        return await update.message.reply_text("Только администраторы могут выдавать роли.")
    role = " ".join(context.args)
    user = update.message.reply_to_message.from_user
    uid = str(user.id)
    entry = user_data.setdefault(uid, {"nickname": user.first_name, "warns":0, "roles":[], "joined": str(datetime.now())})
    if role not in entry["roles"]:
        entry["roles"].append(role)
        save_data()
        await update.message.reply_text(f"Роль '{role}' выдана {user.first_name}.")
    else:
        await update.message.reply_text(f"У {user.first_name} уже есть роль '{role}'.")

async def remove_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("Ответь на сообщение и укажи роль: .удалитьроль <роль>")
    admin_id = update.effective_user.id
    chat_admins = [a.user.id for a in await context.bot.get_chat_administrators(update.effective_chat.id)]
    if admin_id not in chat_admins:
        return await update.message.reply_text("Только администраторы могут удалять роли.")
    role = " ".join(context.args)
    user = update.message.reply_to_message.from_user
    uid = str(user.id)
    entry = user_data.get(uid, {})
    if role in entry.get("roles", []):
        entry["roles"].remove(role)
        save_data()
        await update.message.reply_text(f"Роль '{role}' удалена у {user.first_name}.")
    else:
        await update.message.reply_text("У пользователя нет такой роли.")

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        username = f"@{member.username}" if member.username else member.full_name
        text = f"""
🌘 𝑾𝒆𝒍𝒄𝒐𝒎𝒆 𝒕𝒐 𝒕𝒉𝒆 𝒔𝒊𝒍𝒆𝒏𝒕 𝒔𝒊𝒅𝒆... 🌒  
пρᥙʙᥱᴛᥴᴛʙуᥱʍ ᴛᥱδя, {username}!
... Ты ᴛ᧐᧘ьκ᧐ чᴛ᧐ ᧐ᴛκρы᧘ дʙᥱρь ʙ ʍᥙρ, ᴦдᥱ κᥲждыᥔ х᧐д — ϶ᴛ᧐ ᧐ᴛρᥲжᥱнᥙᥱ ʙ ᧘унн᧐ᥔ ʙ᧐дᥱ - ʙ нᥲɯᥱʍ ᴛёʍн᧐ʍ ᥙ κρᥲᥴᥙʙ᧐ʍ ᥰρ᧐ᥴᴛρᥲнᥴᴛʙᥱ

            ❝ 𝑼𝒏𝒅𝒆𝒓 𝒕𝒉𝒆 𝒎𝒐𝒐𝒏𝒍𝒊𝒈𝒉𝒕 ❞

━━━━━━━━━━━━━━━

╭ ⊹ ꒰ Вᥴя ᥰ᧐᧘ᥱɜнᥲя ᥙнɸ᧐ρʍᥲцᥙя д᧘я н᧐ʙᥙчκ᧐ʙ — нᥙжᥱ.
╰ ⊹  Зᥲдᥲʙᥲᥔ ʙ᧐ᥰρ᧐ʴы, нᥱ δ᧐ᥔᥴя учᥲᥴᴛʙ᧐ʙᥲᴛь ᥙ ᥴᥙяᥔ ʙ нᥲɯᥙх ᥙᴦρᥲх.

Д᧐ ʙᥴᴛρᥱчᥙ нᥲ ᥲρᥱнᥱ, 𝒍𝒖𝒏𝒂𝒓 𝒈𝒖𝒆𝒔𝒕. 🌙
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Information", url="https://t.me/...")],
            [InlineKeyboardButton("🧭 Guide", url="https://t.me/...")],
            [InlineKeyboardButton("🗞 News", url="https://t.me/...")]
        ])
        await update.message.reply_text(text, reply_markup=keyboard)

async def goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.left_chat_member
    name = user.first_name
    text = f"""{name} покидает наш путь под лунным светом. Каждый оставляет след, и твой останется в истории Under the Moonlight 🌒. Спасибо за игру, за участие и за то, что был(а) частью нашей ночной легенды.

𝒏𝒐𝒘… 𝒕𝒉𝒆 𝒎𝒐𝒐𝒏 𝒔𝒉𝒊𝒏𝒆𝒔 𝒇𝒐𝒓 𝒂𝒏𝒐𝒕𝒉𝒆𝒓.

Желаем удачи — где бы ты ни оказался(ась) 🌙"""
    await update.message.reply_text(text)

async def send_cc_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("https://t.me/+dWD8UqTCjGE4YWQ6")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Ответь на сообщение пользователя для инфо.")
    user = update.message.reply_to_message.from_user
    uid = str(user.id)
    data = user_data.get(uid, {})
    nickname = data.get("nickname", user.first_name)
    warns = data.get("warns",0)
    username = f"@{user.username}" if user.username else "Не указано"
    joined = data.get("joined","Неизвестно")
    roles = data.get("roles",[])
    roles_text = "\n".join([f" ├ {r}" for r in roles]) if roles else " └ Нет ролей"
    text = (f"🆔 ID: {user.id}\n👱 Имя: {nickname} (!)\n🌐 @{username}\n➰ Роли:\n{roles_text}\n❕ Варны: {warns}/6\n⤵️ Вступил: {joined}")
    await update.message.reply_text(text)

def main():
    load_data()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r'^\.старт$'), start))
    app.add_handler(MessageHandler(filters.Regex(r'^\.варн$'), warn))
    app.add_handler(MessageHandler(filters.Regex(r'^\.unwarn$'), unwarn))
    app.add_handler(MessageHandler(filters.Regex(r'^\.кик$'), kick))
    app.add_handler(MessageHandler(filters.Regex(r'^\.бан$'), ban))
    app.add_handler(MessageHandler(filters.Regex(r'^\.разбан\b'), unban))
    app.add_handler(MessageHandler(filters.Regex(r'^\.имя\b'), set_name))
    app.add_handler(MessageHandler(filters.Regex(r'^\.ник$'), show_nick))
    app.add_handler(MessageHandler(filters.Regex(r'^\.роль\b'), give_role))
    app.add_handler(MessageHandler(filters.Regex(r'^\.удалитьроль\b'), remove_role))
    app.add_handler(MessageHandler(filters.Regex(r'^\.мы$'), we_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye))
    app.add_handler(MessageHandler(filters.Regex(r'^\.cc$'), send_cc_link))
    app.add_handler(MessageHandler(filters.Regex(r'^\.инфо$'), info))

    app.run_polling()

if __name__ == '__main__':
    main()

