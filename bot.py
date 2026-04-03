import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


# 👇 ТВОЙ ТОКЕН (вставлен)
API_TOKEN = "8661021135:AAG4V822PQWIUSTBDp-UF7aTmSPwNvVRMro"
ADMIN_ID = 8416383800

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ================= FSM =================

class Form(StatesGroup):
    name = State()
    age = State()
    city = State()
    custom_city = State()
    exp = State()
    job = State()
    phone = State()


# ================= КЛАВИАТУРЫ =================

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📩 Залишити заявку")]
    ],
    resize_keyboard=True
)

city_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔥 Київ"), KeyboardButton(text="Львів")],
        [KeyboardButton(text="Одеса"), KeyboardButton(text="Харків")],
        [KeyboardButton(text="Інше місто")]
    ],
    resize_keyboard=True
)

phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Поділитися номером", request_contact=True)]
    ],
    resize_keyboard=True
)


# ================= ХЕНДЛЕРЫ =================

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привіт! Допоможу знайти роботу 🇺🇦",
        reply_markup=start_kb
    )


@dp.message(lambda msg: msg.text == "📩 Залишити заявку")
async def start_form(message: types.Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("Введіть ваше ім'я:")


# -------- ИМЯ --------
@dp.message(Form.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.age)
    await message.answer("Ваш вік:")


# -------- ВОЗРАСТ --------
@dp.message(Form.age)
async def get_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введіть коректний вік (число):")
        return

    await state.update_data(age=message.text)
    await state.set_state(Form.city)
    await message.answer("Оберіть ваше місто:", reply_markup=city_kb)


# -------- ГОРОД --------
@dp.message(Form.city)
async def get_city(message: types.Message, state: FSMContext):
    if message.text == "Інше місто":
        await state.set_state(Form.custom_city)
        await message.answer("Введіть ваше місто:")
        return

    await state.update_data(city=message.text)
    await state.set_state(Form.exp)
    await message.answer("Досвід роботи:")


@dp.message(Form.custom_city)
async def get_custom_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(Form.exp)
    await message.answer("Досвід роботи:")


# -------- ОПЫТ --------
@dp.message(Form.exp)
async def get_exp(message: types.Message, state: FSMContext):
    await state.update_data(exp=message.text)
    await state.set_state(Form.job)
    await message.answer("Яка робота вас цікавить?")


# -------- РАБОТА --------
@dp.message(Form.job)
async def get_job(message: types.Message, state: FSMContext):
    await state.update_data(job=message.text)
    await state.set_state(Form.phone)

    await message.answer(
        "Натисніть кнопку нижче, щоб поділитися номером:",
        reply_markup=phone_kb
    )


# -------- ТЕЛЕФОН --------
@dp.message(Form.phone)
async def get_phone(message: types.Message, state: FSMContext):
    if not message.contact:
        await message.answer("Натисніть кнопку для відправки номера 👇", reply_markup=phone_kb)
        return

    data = await state.get_data()
    data["phone"] = message.contact.phone_number

    city = data["city"].lower()

    if "київ" in city or "киев" in city or "🔥" in city:
        prefix = "🔥 ПРІОРИТЕТ (Київ)"
    else:
        prefix = "🆕 Нова заявка"

    text = f"""
{prefix}

👤 Ім'я: {data['name']}
🎂 Вік: {data['age']}
📍 Місто: {data['city']}
💼 Досвід: {data['exp']}
📌 Робота: {data['job']}
📱 Телефон: {data['phone']}
"""

    await bot.send_message(ADMIN_ID, text)

    await message.answer(
        "✅ Дякуємо! Заявку прийнято",
        reply_markup=start_kb
    )

    await state.clear()


# ================= ЗАПУСК =================

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())