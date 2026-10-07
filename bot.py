import os
import random
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]
TZ = ZoneInfo("Europe/Moscow")
DB = "bot.db"

REGIONS = {
    "01": "Республика Адыгея",
    "02": "Республика Башкортостан",
    "03": "Республика Бурятия",
    "04": "Республика Алтай",
    "05": "Республика Дагестан",
    "06": "Республика Ингушетия",
    "07": "Кабардино-Балкарская Республика",
    "08": "Республика Калмыкия",
    "09": "Карачаево-Черкесская Республика",
    "10": "Республика Карелия",
    "11": "Республика Коми",
    "12": "Республика Марий Эл",
    "13": "Республика Мордовия",
    "14": "Республика Саха (Якутия)",
    "15": "Республика Северная Осетия — Алания",
    "16": "Республика Татарстан",
    "17": "Республика Тыва",
    "18": "Удмуртская Республика",
    "19": "Республика Хакасия",
    "21": "Чувашская Республика",
    "22": "Алтайский край",
    "23": "Краснодарский край",
    "24": "Красноярский край",
    "25": "Приморский край",
    "26": "Ставропольский край",
    "27": "Хабаровский край",
    "28": "Амурская область",
    "29": "Архангельская область",
    "30": "Астраханская область",
    "31": "Белгородская область",
    "32": "Брянская область",
    "33": "Владимирская область",
    "34": "Волгоградская область",
    "35": "Вологодская область",
    "36": "Воронежская область",
    "37": "Ивановская область",
    "38": "Иркутская область",
    "39": "Калининградская область",
    "40": "Калужская область",
    "41": "Камчатский край",
    "42": "Кемеровская область",
    "43": "Кировская область",
    "44": "Костромская область",
    "45": "Курганская область",
    "46": "Курская область",
    "47": "Ленинградская область",
    "48": "Липецкая область",
    "49": "Магаданская область",
    "50": "Московская область",
    "51": "Мурманская область",
    "52": "Нижегородская область",
    "53": "Новгородская область",
    "54": "Новосибирская область",
    "55": "Омская область",
    "56": "Оренбургская область",
    "57": "Орловская область",
    "58": "Пензенская область",
    "59": "Пермский край",
    "60": "Псковская область",
    "61": "Ростовская область",
    "62": "Рязанская область",
    "63": "Самарская область",
    "64": "Саратовская область",
    "65": "Сахалинская область",
    "66": "Свердловская область",
    "67": "Смоленская область",
    "68": "Тамбовская область",
    "69": "Тверская область",
    "70": "Томская область",
    "71": "Тульская область",
    "72": "Тюменская область",
    "73": "Ульяновская область",
    "74": "Челябинская область",
    "75": "Забайкальский край",
    "76": "Ярославская область",
    "77": "Москва",
    "78": "Санкт-Петербург",
    "79": "Еврейская автономная область",
    "80": "Донецкая Народная Республика",
    "81": "Луганская Народная Республика",
    "82": "Республика Крым",
    "83": "Ненецкий автономный округ",
    "84": "Херсонская область",
    "85": "Запорожская область",
    "86": "Ханты-Мансийский автономный округ — Югра",
    "87": "Чукотский автономный округ",
    "89": "Ямало-Ненецкий автономный округ",
    "92": "Севастополь",
    "94": "Байконур",
    "95": "Чеченская Республика",
}

EXTRA = {
    "02": ["102", "702"],
    "03": ["103"],
    "09": ["109"],
    "13": ["113"],
    "16": ["116", "716"],
    "18": ["118"],
    "21": ["121"],
    "22": ["122", "222"],
    "23": ["93", "123", "193", "323"],
    "24": ["124", "224"],
    "25": ["125", "725"],
    "26": ["126"],
    "30": ["130"],
    "31": ["131"],
    "34": ["134"],
    "36": ["136"],
    "38": ["138"],
    "39": ["139"],
    "42": ["142"],
    "50": ["90", "150", "550", "750", "790"],
    "52": ["152", "252"],
    "54": ["154", "754"],
    "55": ["155"],
    "56": ["156"],
    "58": ["158"],
    "59": ["159"],
    "61": ["161", "761"],
    "63": ["163", "763"],
    "64": ["164"],
    "66": ["96", "196"],
    "69": ["169"],
    "72": ["172"],
    "73": ["173"],
    "74": ["174", "774"],
    "77": ["97", "99", "177", "197", "199", "777", "797", "799", "977", "997"],
    "78": ["98", "178", "198", "778"],
    "80": ["180"],
    "81": ["181"],
    "82": ["182"],
    "84": ["184"],
    "85": ["185"],
    "86": ["186"],
    "92": ["192"],
}

for base, extras in EXTRA.items():
    for code in extras:
        REGIONS[code] = REGIONS[base]

MENU = ReplyKeyboardMarkup(
    [
        ["🎲 Случайные 5", "🔎 Найти код"],
        ["📋 Все коды", "🧠 Викторина"],
        ["📊 Статистика", "⏰ Настроить время"],
    ],
    resize_keyboard=True,
)

def db():
    return sqlite3.connect(DB)

def init_db():
    with db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                morning_enabled INTEGER DEFAULT 1,
                morning_hour INTEGER DEFAULT 7,
                morning_minute INTEGER DEFAULT 0,
                quiz_total INTEGER DEFAULT 0,
                quiz_correct INTEGER DEFAULT 0,
                quiz_streak INTEGER DEFAULT 0,
                best_streak INTEGER DEFAULT 0
            )
        """)

def add_user(chat_id):
    with db() as con:
        con.execute(
            "INSERT OR IGNORE INTO users(chat_id) VALUES (?)",
            (chat_id,)
        )

def get_user(chat_id):
    with db() as con:
        return con.execute(
            "SELECT * FROM users WHERE chat_id=?",
            (chat_id,)
        ).fetchone()

def set_morning(chat_id, enabled=None, hour=None, minute=None):
    add_user(chat_id)

    with db() as con:
        if enabled is not None:
            con.execute(
                "UPDATE users SET morning_enabled=? WHERE chat_id=?",
                (int(enabled), chat_id)
            )

        if hour is not None:
            con.execute(
                "UPDATE users SET morning_hour=? WHERE chat_id=?",
                (hour, chat_id)
            )

        if minute is not None:
            con.execute(
                "UPDATE users SET morning_minute=? WHERE chat_id=?",
                (minute, chat_id)
            )

def users_for_time(hour, minute):
    with db() as con:
        return [
            row[0]
            for row in con.execute(
                """
                SELECT chat_id
                FROM users
                WHERE morning_enabled=1
                AND morning_hour=?
                AND morning_minute=?
                """,
                (hour, minute)
            )
        ]

def update_stats(chat_id, correct):
    add_user(chat_id)

    with db() as con:
        row = con.execute(
            """
            SELECT quiz_total, quiz_correct, quiz_streak, best_streak
            FROM users
            WHERE chat_id=?
            """,
            (chat_id,)
        ).fetchone()

        total, good, streak, best = row

        total += 1

        if correct:
            good += 1
            streak += 1
            best = max(best, streak)
        else:
            streak = 0

        con.execute(
            """
            UPDATE users
            SET quiz_total=?,
                quiz_correct=?,
                quiz_streak=?,
                best_streak=?
            WHERE chat_id=?
            """,
            (total, good, streak, best, chat_id)
        )

        return total, good, streak, best

def random_message():
    selected = random.sample(list(REGIONS.items()), 5)

    return (
        "Доброе утро! ☀️\n\n"
        + "\n".join(
            f"{code} — {name}"
            for code, name in selected
        )
    )

def all_codes_text():
    items = sorted(
        REGIONS.items(),
        key=lambda x: (len(x[0]), x[0])
    )

    return (
        "📋 Коды регионов:\n\n"
        + "\n".join(
            f"{code} — {name}"
            for code, name in items
        )
    )

def find_code(code):
    code = code.strip().upper()

    if code in REGIONS:
        return f"🔎 {code} — {REGIONS[code]}"

    return "❌ Такой код не найден в базе."

def quiz_keyboard(options):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                option,
                callback_data=f"quiz:{option}"
            )
        ]
        for option in options
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_chat.id)

    await update.message.reply_text(
        "Готово! 🌅\n\n"
        "Я буду присылать утреннюю подборку в выбранное время.\n\n"
        "Также здесь есть поиск кодов, список, "
        "викторина и статистика.",
        reply_markup=MENU,
    )

async def now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_chat.id)

    await update.message.reply_text(
        random_message(),
        reply_markup=MENU,
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_morning(
        update.effective_chat.id,
        enabled=False
    )

    await update.message.reply_text(
        "Утренняя рассылка отключена. 🔕\n\n"
        "Нажми «⏰ Настроить время», "
        "чтобы включить её снова.",
        reply_markup=MENU,
    )

async def code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Напиши код после команды.\n\n"
            "Например: /code 37"
        )
        return

    await update.message.reply_text(
        find_code(context.args[0]),
        reply_markup=MENU,
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    row = get_user(update.effective_chat.id)

    if not row:
        add_user(update.effective_chat.id)
        row = get_user(update.effective_chat.id)

    (
        _,
        enabled,
        hour,
        minute,
        total,
        good,
        streak,
        best,
    ) = row

    percent = round(good / total * 100) if total else 0

    status = (
        f"{hour:02d}:{minute:02d}"
        if enabled
        else "выключена"
    )

    await update.message.reply_text(
        f"📊 Твоя статистика\n\n"
        f"Ответов: {total}\n"
        f"Правильных: {good}\n"
        f"Точность: {percent}%\n"
        f"Текущая серия: {streak}\n"
        f"Лучшая серия: {best}\n\n"
        f"🌅 Рассылка: {status}",
        reply_markup=MENU,
    )

async def time_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "07:00",
                callback_data="time:7:0"
            ),
            InlineKeyboardButton(
                "08:00",
                callback_data="time:8:0"
            ),
            InlineKeyboardButton(
                "09:00",
                callback_data="time:9:0"
            ),
        ],
        [
            InlineKeyboardButton(
                "10:00",
                callback_data="time:10:0"
            ),
            InlineKeyboardButton(
                "18:00",
                callback_data="time:18:0"
            ),
            InlineKeyboardButton(
                "🔕 Выключить",
                callback_data="time:off"
            ),
        ],
    ])

    await update.message.reply_text(
        "⏰ Выбери время утренней рассылки по Москве:",
        reply_markup=keyboard,
    )

def new_quiz(context):
    correct_code, correct_name = random.choice(
        list(REGIONS.items())
    )

    distractors = random.sample(
        [
            name
            for code, name in REGIONS.items()
            if code != correct_code
        ],
        3,
    )

    options = [correct_name] + distractors
    random.shuffle(options)

    context.user_data["quiz_correct"] = correct_name

    return correct_code, options

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code, options = new_quiz(context)

    await update.message.reply_text(
        f"🧠 Викторина!\n\n"
        f"Какому региону соответствует код {code}?",
        reply_markup=quiz_keyboard(options),
    )

async def quiz_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    chosen = query.data.split(":", 1)[1]
    correct = context.user_data.get("quiz_correct")

    if not correct:
        await query.edit_message_text(
            "Начни новую викторину кнопкой «🧠 Викторина»."
        )
        return

    is_correct = chosen == correct

    total, good, streak, best = update_stats(
        query.message.chat_id,
        is_correct,
    )

    if is_correct:
        text = (
            f"✅ Правильно!\n\n"
            f"{correct}\n\n"
            f"🔥 Серия: {streak}"
        )
    else:
        text = (
            f"❌ Неправильно.\n\n"
            f"Правильный ответ: {correct}\n\n"
            f"Серия сброшена.\n"
            f"Всего правильных: {good}/{total}"
        )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➡️ Следующий вопрос",
                callback_data="quiz_next"
            )
        ]
    ])

    context.user_data.pop("quiz_correct", None)

    await query.edit_message_text(
        text,
        reply_markup=keyboard,
    )

async def quiz_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    code, options = new_quiz(context)

    await query.edit_message_text(
        f"🧠 Какому региону соответствует код {code}?",
        reply_markup=quiz_keyboard(options),
    )

async def time_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    if query.data == "time:off":
        set_morning(
            query.message.chat_id,
            enabled=False
        )

        await query.edit_message_text(
            "🔕 Утренняя рассылка отключена."
        )
        return

    _, hour, minute = query.data.split(":")

    set_morning(
        query.message.chat_id,
        enabled=True,
        hour=int(hour),
        minute=int(minute),
    )

    await query.edit_message_text(
        f"✅ Готово!\n\n"
        f"Буду присылать подборку каждый день "
        f"в {int(hour):02d}:{int(minute):02d} "
        f"по Москве."
    )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🎲 Случайные 5":
        await now(update, context)

    elif text == "🔎 Найти код":
        await update.message.reply_text(
            "Напиши код, например: 37"
        )
        context.user_data["waiting_code"] = True

    elif text == "📋 Все коды":
        await update.message.reply_text(
            all_codes_text(),
            reply_markup=MENU,
        )

    elif text == "🧠 Викторина":
        await quiz(update, context)

    elif text == "📊 Статистика":
        await stats(update, context)

    elif text == "⏰ Настроить время":
        await time_menu(update, context)

    elif context.user_data.get("waiting_code"):
        context.user_data.pop("waiting_code", None)

        await update.message.reply_text(
            find_code(text),
            reply_markup=MENU,
        )

async def morning_job(context: ContextTypes.DEFAULT_TYPE):
    now_moscow = datetime.now(TZ)

    hour = now_moscow.hour
    minute = now_moscow.minute

    for chat_id in users_for_time(hour, minute):
        try:
            await context.bot.send_message(
                chat_id,
                random_message()
            )
        except Exception as e:
            print(e)

def main():
    init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("now", now)
    )

    app.add_handler(
        CommandHandler("stop", stop)
    )

    app.add_handler(
        CommandHandler("code", code_command)
    )

    app.add_handler(
        CommandHandler("stats", stats)
    )

    app.add_handler(
        CommandHandler("quiz", quiz)
    )

    app.add_handler(
        CallbackQueryHandler(
            time_choice,
            pattern=r"^time:"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            quiz_next,
            pattern=r"^quiz_next$"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            quiz_choice,
            pattern=r"^quiz:"
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )

    app.job_queue.run_repeating(
        morning_job,
        interval=60,
        first=5
    )

    print("Bot started")

    app.run_polling()

if __name__ == "__main__":
    main()
