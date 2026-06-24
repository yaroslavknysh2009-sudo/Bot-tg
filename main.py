import telebot
from telebot import types
import json
import os

TOKEN = '8882545649:AAHro2kI0AAE-pQcjJia_25hc7atDuolBC8'
bot = telebot.TeleBot(TOKEN)

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
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        char = Character()
        char.__dict__.update(data)
        return char
    return Character(name=f"Герой")

def save_user(chat_id, char):
    filename = f"char_{chat_id}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(char.__dict__, f, ensure_ascii=False, indent=4)

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_stats = types.KeyboardButton("📊 Мой статус")
    btn_push = types.KeyboardButton("🤸 Отжался")
    btn_pull = types.KeyboardButton("🏋️ Подтянулся")
    btn_squat = types.KeyboardButton("🦵 Присел")
    btn_read = types.KeyboardButton("📖 Почитал")
    btn_warmup = types.KeyboardButton("☀️ Сделал зарядку")
    btn_run = types.KeyboardButton("🏃 Побегал")
    
    markup.add(btn_stats)
    markup.add(btn_push, btn_pull, btn_squat)
    markup.add(btn_read, btn_warmup, btn_run)
    return markup

@bot.message_handler(commands=['start'])
def start_game(message):
    chat_id = message.chat.id
    USERS[chat_id] = load_user(chat_id)
    bot.send_message(chat_id, "Привет! Твой личный трекер прокачки готов к работе. Выбери действие:", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    chat_id = message.chat.id
    if chat_id not in USERS:
        USERS[chat_id] = load_user(chat_id)
        
    player = USERS[chat_id]

    if message.text == "📊 Мой статус":
        bot.send_message(chat_id, player.get_stats_text())
        
    elif message.text in ["🤸 Отжался", "🏋️ Подтянулся", "🦵 Присел", "📖 Почитал"]:
        action_map = {
            "🤸 Отжался": ("Сколько раз отжался?", "pushups"),
            "🏋️ Подтянулся": ("Сколько раз подтянулся?", "pullups"),
            "🦵 Присел": ("Сколько раз присел?", "squats"),
            "📖 Почитал": ("Сколько страниц прочитал?", "reading")
        }
        text, action_type = action_map[message.text]
        msg = bot.send_message(chat_id, text)
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
    player = USERS[chat_id]
    
    try:
        val = int(message.text)
        if val <= 0:
            bot.send_message(chat_id, "Число должно быть больше нуля!")
            return

        if action_type == "pushups":
            res = player.add_pushups(val)
        elif action_type == "pullups":
            res = player.add_pullups(val)
        elif action_type == "squats":
            res = player.add_squats(val)
        elif action_type == "reading":
            res = player.add_reading(val)

        save_user(chat_id, player)
        bot.send_message(chat_id, res, reply_markup=main_keyboard())
        
    except ValueError:
        bot.send_message(chat_id, "❌ Ошибка! Введи обычное целое число.", reply_markup=main_keyboard())

print("Бот успешно запущен и ждет тренировок...")
bot.infinity_polling()

