import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

import config

# Включаем логирование
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Функция загрузки контента из JSON
def load_content():
    with open("content.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Функция генерации инлайн-клавиатуры под сообщениями на основе данных из JSON
def get_keyboard(step_data):
    builder = InlineKeyboardBuilder()
    if "buttons" in step_data:
        for row in step_data["buttons"]:
            row_buttons = []
            for btn in row:
                if "url" in btn:
                    row_buttons.append(types.InlineKeyboardButton(text=btn["text"], url=btn["url"]))
                else:
                    row_buttons.append(types.InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"]))
            builder.row(*row_buttons)
    return builder.as_markup()

# Функция создания постоянного Главного Меню (Reply-кнопки внизу экрана)
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🚀 Start Learning"))
    builder.row(types.KeyboardButton(text="📊 Daily Analytics"), types.KeyboardButton(text="🛠 Support"))
    builder.row(types.KeyboardButton(text="❓ Help"))
    return builder.as_markup(resize_keyboard=True)

# Команда /start — убираем pre_start, включаем главное меню и сразу присылаем первый пост
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    content = load_content()
    step_data = content["post_1"] # Начинаем сразу с post_1
    
    # 1. Отправляем приветствие и активируем постоянное нижнее меню
    await message.answer(
        text="Welcome to the Tick Tape educational bot!",
        reply_markup=get_main_menu()
    )
    # 2. Отдельным сообщением присылаем текст первого поста с его инлайн-кнопками
    await message.answer(
        text=step_data["text"],
        reply_markup=get_keyboard(step_data),
        disable_web_page_preview=True
    )

# --- ОБРАБОТКА НАЖАТИЙ КНОПОК НИЖНЕГО ГЛАВНОГО МЕНЮ ---

@dp.message(F.text == "🚀 Start Learning")
async def menu_start_learning(message: types.Message):
    content = load_content()
    step_data = content["post_1"]
    await message.answer(
        text=step_data["text"],
        reply_markup=get_keyboard(step_data),
        disable_web_page_preview=True
    )

@dp.message(F.text == "📊 Daily Analytics")
async def menu_analytics(message: types.Message):
    # Так как обычная репли-кнопка не может содержать прямую ссылку, выдаем её сообщением
    await message.answer(
        text="📊 Access our daily analytics channel here:\n👉 https://t.me/your_channel_link",
        disable_web_page_preview=True
    )

@dp.message(F.text == "❓ Help")
async def menu_help(message: types.Message):
    content = load_content()
    step_data = content["sys_help"]
    await message.answer(text=step_data["text"], reply_markup=get_keyboard(step_data))

@dp.message(F.text == "🛠 Support")
async def menu_support(message: types.Message):
    content = load_content()
    step_data = content["sys_support"]
    await message.answer(text=step_data["text"], reply_markup=get_keyboard(step_data))

# --- ОБРАБОТКА ИНЛАЙН-КНОПОК (ПЕРЕХОДЫ С ДОБАВЛЕНИЕМ В ЛЕНТУ) ---

# Хэндлер переходов по шагам обучения
@dp.callback_query(F.data.startswith("step:"))
async def handle_steps(callback: types.CallbackQuery):
    step_name = callback.data.split(":")[1]
    content = load_content()
    
    if step_name in content:
        step_data = content[step_name]
        # Используем .answer() вместо .edit_text(), чтобы новые посты ложились в ленту ниже
        await callback.message.answer(
            text=step_data["text"],
            reply_markup=get_keyboard(step_data),
            disable_web_page_preview=True
        )
    await callback.answer()

# Хэндлер для доп. разделов (Help / Support) через инлайн-кнопки
@dp.callback_query(F.data.startswith("sys:"))
async def handle_sys_steps(callback: types.CallbackQuery):
    sys_action = callback.data.split(":")[1]
    content = load_content()
    key = f"sys_{sys_action}"
    
    if key in content:
        step_data = content[key]
        # Используем .answer() вместо .edit_text()
        await callback.message.answer(
            text=step_data["text"],
            reply_markup=get_keyboard(step_data)
        )
    await callback.answer()

async def main():
    print("Робот Tick Tape запущен и готов к размотке графиков...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
