import os
from threading import Thread
from flask import Flask
import telebot
from telebot import types
import json
import glob

app = Flask('')

@app.route('/')
def home():
    return "Бот запущен и работает!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

TOKEN = '8882545649:AAHro2kI0AAE-pQcjJia_25hc7atDuolBC8'
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = -1004352455151  

class Character:
    def __init__(self, name="Герой"):
        self.name = name
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 100
        self.strength = 10.0
        self.intelligence = 10.0
        self.endurance = 10.0
        self.total_pushups = 0
        self.total_pullups = 0
        self.total_squats = 0
        self.total_pages = 0
        self.total_warmups = 0
        self.total_runs = 0

    def check_levelup(self):
        messages = []
        while self.exp >= self.exp_to_next_level:
            self.exp -= self.exp_to_next_level
            self.level += 1
            self.exp_to_next_level = int(self.exp_to_next_level * 1.2)
            messages.append(f"🎉 ЛЕВЕЛ-АП! Вы достигли {self.level} уровня! 🎉")
        return "\n".join(messages) if messages else None

    def add_pushups(self, reps):
        gained_str = reps / 10.0
        gained_exp = reps * 2
        self.strength += gained_str
        self.exp += gained_exp
        self.total_pushups += reps
        msg = f"💪 Отжимания: +{gained_exp} XP, Сила +{gained_str:.1f}"
        lvl_msg = self.check_levelup()
        return f"{msg}\n{lvl_msg}" if lvl_msg else msg

    def add_pullups(self, reps):
        gained_str = reps / 5.0
        gained_exp = reps * 4
        self.strength += gained_str
        self.exp += gained_exp
        self.total_pullups += reps
        msg = f"💪 Подтягивания: +{gained_exp} XP, Сила +{gained_str:.1f}"
        lvl_msg = self.check_levelup()
        return f"{msg}\n{lvl_msg}" if lvl_msg else msg

    def add_squats(self, reps):
        gained_val = reps / 20.0
        gained_exp = int(reps * 2.5)
        self.strength += gained_val
        self.endurance += gained_val
        self.exp += gained_exp
        self.total_squats += reps
        msg = f"🦵 Приседания: +{gained_exp} XP, Сила +{gained_val:.2f}, Выносливость +{gained_val:.2f}"
        lvl_msg = self.check_levelup()
        return f"{msg}\n{lvl_msg}" if lvl_msg else msg

    def add_reading(self, pages):
        gained_int = pages / 10.0
        gained_exp = pages * 3
        self.intelligence += gained_int
        self.exp += gained_exp
        self.total_pages += pages
        msg = f"📚 Чтение: +{gained_exp} XP, Интеллект +{gained_int:.1f}"
        lvl_msg = self.check_levelup()
        return f"{msg}\n{lvl_msg}" if lvl_msg else msg

    def add_warmup(self):
        self.endurance += 3.0
        self.exp += 15
        self.total_warmups += 1
        msg = f"🤸 Зарядка выполнена! +15 XP, Выносливость +3.0"
        lvl_msg = self.check_levelup()
        return f"{msg}\n{lvl_msg}" if lvl_msg else msg

    def add_run(self):
        self.endurance += 5.0
        self.exp += 30
        self.total_runs += 1
        msg = f"🏃 Пробежка выполнена! +30 XP, Выносливость +5.0"
        lvl_msg = self.check_levelup()
        return f"{msg}\n{lvl_msg}" if lvl_msg else msg

    def get_stats_text(self):
        return (f"⚔️ Персонаж: {self.name}\n"
                f"⭐ Уровень: {self.level}\n"
                f"✨ Опыт: {self.exp}/{self.exp_to_next_level} XP\n"
                f"──────────────────\n"
                f"💪 Сила: {self.strength:.2f}\n"
                f"🧠 Интеллект: {self.intelligence:.1f}\n"
                f"🔋 Выносливость: {self.endurance:.2f}\n"
                f"──────────────────\n"
                f"📊 Всего за историю:\n"
                f"🤸 Отжиманий: {self.total_pushups}\n"
                f"🏋️ Подтягиваний: {self.total_pullups}\n"
                f"🦵 Приседаний: {self.total_squats}\n"
                f"📖 Страниц прочитано: {self.total_pages}\n"
                f"☀️ Зарядок сделано: {self.total_warmups}\n"
                f"👟 Пробежек совершено: {self.total_runs}")

USERS = {}

def load_user(chat_id):
    filename = f"char_{chat_id}.json"
    
    # 1. Проверяем локальный файл
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            char = Character()
            char.__dict__.update(data)
            return char
        except Exception as e:
            print(f"Ошибка локального файла: {e}")
        
    # 2. Восстановление из истории группы (поиск по ID пользователя)
    try:
        print(f"Ищу локальный бэкап в истории для {chat_id}...")
        restored_data = restore_from_telegram_history(chat_id)
        if restored_data:
            char = Character()
            char.__dict__.update(restored_data)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(char.__dict__, f, ensure_ascii=False, indent=4)
            return char
    except Exception as e:
        print(f"Не удалось восстановить из истории: {e}")
        
    return Character(name="Герой")

def save_user(chat_id, char):
    filename = f"char_{chat_id}.json"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(char.__dict__, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения файла: {e}")
    
    backup_to_telegram(chat_id, char)

def backup_to_telegram(chat_id, char):
    try:
        json_str = json.dumps(char.__dict__, ensure_ascii=False)
        backup_msg = f"#BACKUP_ID_{chat_id}#\n{json_str}"
        # Просто отправляем в группу, БЕЗ закрепов
        bot.send_message(ADMIN_ID, backup_msg)
    except Exception as e:
        print(f"Ошибка создания бэкапа: {e}")

def restore_from_telegram_history(target_chat_id):
    try:
        # Чтобы обойти Privacy Mode, временно используем безопасный перебор последних сообщений
        # Бот гарантированно прочитает свои же сообщения, которые он отправлял в этот чат
        updates = bot.get_updates(limit=100, allowed_updates=["message"])
        
        # Если через updates не вышло, используем прямой запрос истории (убедись, что Privacy Mode выключен по инструкции ранее)
        messages = bot.get_chat_history(ADMIN_ID, limit=100)
        if messages:
            marker = f"#BACKUP_ID_{target_chat_id}#"
            for msg in messages:
                if msg.text and msg.text.startswith(marker):
                    json_part = msg.text.replace(marker, "").strip()
                    return json.loads(json_part)
    except Exception as e:
        print(f"Ошибка чтения истории: {e}")
    return None

def get_leaderboard_text():
    user_files = glob.glob("char_*.json")
    players = []
    for file in user_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                players.append({
                    "name": data.get("name", "Герой"),
                    "level": data.get("level", 1),
                    "exp": data.get("exp", 0),
                    "strength": data.get("strength", 10.0),
                    "intelligence": data.get("intelligence", 10.0),
                    "endurance": data.get("endurance", 10.0)
                })
        except Exception:
            continue
            
    if not players:
        return "🏆 Доска лидеров пока пуста!"
        
    players.sort(key=lambda x: (x["level"], x["exp"]), reverse=True)
    leaderboard = ["🏆 **ДОСКА ЛИДЕРОВ** 🏆\n──────────────────"]
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    
    for index, p in enumerate(players):
        medal = medals.get(index, "👤")
        leaderboard.append(
            f"{medal} {index+1}. **{p['name']}** — {p['level']} lvl\n"
            f"└ 💪 Сил: {p['strength']:.1f} | 🧠 Инт: {p['intelligence']:.1f} | 🔋 Вын: {p['endurance']:.1f}\n"
            f"──────────────────"
        )
    return "\n".join(leaderboard)

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📊 Мой статус"), types.KeyboardButton("🏆 Доска лидеров"))
    markup.add(types.KeyboardButton("🤸 Отжался"), types.KeyboardButton("🏋️ Подтянулся"), types.KeyboardButton("🦵 Присел"))
    markup.add(types.KeyboardButton("📖 Почитал"), types.KeyboardButton("☀️ Сделал зарядку"), types.KeyboardButton("🏃 Побегал"))
    return markup

@bot.message_handler(commands=['start'])
def start_game(message):
    chat_id = message.chat.id
    USERS[chat_id] = load_user(chat_id)
    bot.send_message(
        chat_id, 
        f"Привет, {message.from_user.first_name}! Твой прогресс успешно загружен.\n\n"
        "💡 Чтобы изменить имя в топе, напиши: `/name ТвоеИмя`", 
        reply_markup=main_keyboard(), 
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['name'])
def change_name(message):
    chat_id = message.chat.id
    if chat_id not in USERS:
        USERS[chat_id] = load_user(chat_id)
    player = USERS[chat_id]
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(chat_id, "❌ Укажи имя через пробел.")
        return
    player.name = parts[1].strip()
    save_user(chat_id, player)
    bot.send_message(chat_id, f"✅ Имя изменено на: **{player.name}**", parse_mode="Markdown", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    chat_id = message.chat.id
    if chat_id not in USERS:
        USERS[chat_id] = load_user(chat_id)
    player = USERS[chat_id]

    if message.text == "📊 Мой статус":
        bot.send_message(chat_id, player.get_stats_text())
    elif message.text == "🏆 Доска лидеров":
        bot.send_message(chat_id, get_leaderboard_text(), parse_mode="Markdown")
    elif message.text in ["🤸 Отжался", "🏋️ Подтянулся", "🦵 Присел", "📖 Почитал"]:
        action_map = {
            "🤸 Отжался": ("Сколько раз отжался?", "pushups"),
            "🏋️ Подтянулся": ("Сколько раз подтянулся?", "pullups"),
            "🦵 Присел": ("Сколько раз присел?", "squats"),
            "📖 Почитал": ("Сколько страниц прочитал?", "reading")
        }
        text, action_type = action_map[message.text]
        msg = bot.send_message(chat_id, text, reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, process_input, action_type)
    elif message.text == "☀️ Сделал зарядку":
        res = player.add_warmup()
        save_user(chat_id, player)
        bot.send_message(chat_id, res, reply_markup=main_keyboard())
    elif message.text == "🏃 Побегал":
        res = player.add_run()
        save_user(chat_id, player)
        bot.send_message(chat_id, res, reply_markup=main_keyboard())

def process_input(message, action_type):
    chat_id = message.chat.id
    if chat_id not in USERS:
        USERS[chat_id] = load_user(chat_id)
    player = USERS[chat_id]
    try:
        val = int(message.text)
        if val <= 0:
            bot.send_message(chat_id, "Введи число больше 0!", reply_markup=main_keyboard())
            return
        if action_type == "pushups": res = player.add_pushups(val)
        elif action_type == "pullups": res = player.add_pullups(val)
        elif action_type == "squats": res = player.add_squats(val)
        elif action_type == "reading": res = player.add_reading(val)
        save_user(chat_id, player)
        bot.send_message(chat_id, res, reply_markup=main_keyboard())
    except ValueError:
        bot.send_message(chat_id, "❌ Введи целое число.", reply_markup=main_keyboard())

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    bot.infinity_polling(timeout=15, long_polling_timeout=5)
