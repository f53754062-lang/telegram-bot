import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8416383800

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_data = {}

# стартовая клавиатура
start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📩 Залишити заявку")]
    ],
    resize_keyboard=True
)

# клавиатура городов
city_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔥 Київ"), KeyboardButton(text="Львів")],
        [KeyboardButton(text="Одеса"), KeyboardButton(text="Харків")],
        [KeyboardButton(text="Інше місто")]
    ],
    resize_keyboard=True
)

# кнопка телефона
phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Поділитися номером", request_contact=True)]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Привіт! Допоможу знайти роботу 🇺🇦",
        reply_markup=start_kb
    )

@dp.message()
async def handle(message: types.Message):
    user_id = message.from_user.id

    # защита от бага (если не начал анкету)
    if user_id not in user_data and message.text != "📩 Залишити заявку":
        await message.answer("Натисніть кнопку нижче, щоб почати 👇", reply_markup=start_kb)
        return

    # старт анкеты
    if message.text == "📩 Залишити заявку":
        user_data[user_id] = {}
        await message.answer("Введіть ваше ім'я:")

    # имя
    elif user_id in user_data and "name" not in user_data[user_id]:
        user_data[user_id]["name"] = message.text
        await message.answer("Ваш вік:")

    # возраст
    elif user_id in user_data and "age" not in user_data[user_id]:
        user_data[user_id]["age"] = message.text
        await message.answer("Оберіть ваше місто:", reply_markup=city_kb)

    # выбор города
    elif user_id in user_data and "city" not in user_data[user_id]:
        if message.text == "Інше місто":
            user_data[user_id]["custom_city"] = True
            await message.answer("Введіть ваше місто:")
            return
        else:
            user_data[user_id]["city"] = message.text
            await message.answer("Досвід роботи:")

    # ввод другого города
    elif user_data[user_id].get("custom_city") and "city" not in user_data[user_id]:
        user_data[user_id]["city"] = message.text
        user_data[user_id].pop("custom_city")
        await message.answer("Досвід роботи:")

    # опыт
    elif user_id in user_data and "exp" not in user_data[user_id]:
        user_data[user_id]["exp"] = message.text
        await message.answer("Яка робота вас цікавить?")

    # желаемая работа
    elif user_id in user_data and "job" not in user_data[user_id]:
        user_data[user_id]["job"] = message.text
        await message.answer(
            "Натисніть кнопку нижче, щоб поділитися номером:",
            reply_markup=phone_kb
        )

    # получение телефона
    elif user_id in user_data and "phone" not in user_data[user_id]:
        if message.contact:
            user_data[user_id]["phone"] = message.contact.phone_number
        else:
            await message.answer(
                "Будь ласка, натисніть кнопку для відправки номера 👇",
                reply_markup=phone_kb
            )
            return

        city = user_data[user_id]["city"].lower()

        if "київ" in city or "киев" in city or "🔥" in city:
            prefix = "🔥 ПРІОРИТЕТ (Київ)"
        else:
            prefix = "🆕 Нова заявка"

        text = f"""
{prefix}

👤 Ім'я: {user_data[user_id]['name']}
🎂 Вік: {user_data[user_id]['age']}
📍 Місто: {user_data[user_id]['city']}
💼 Досвід: {user_data[user_id]['exp']}
📌 Робота: {user_data[user_id]['job']}
📱 Телефон: {user_data[user_id]['phone']}
"""

        # отправка админу
        await bot.send_message(ADMIN_ID, text)

        await message.answer(
            "✅ Дякуємо! Заявку прийнято",
            reply_markup=start_kb
        )

        user_data.pop(user_id)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())