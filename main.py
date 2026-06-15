import asyncio
import json
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config

# Включаем логирование
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Функция загрузки контента из JSON
def load_content():
    with open("content.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Функция генерации инлайн-клавиатуры на основе данных из JSON
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

# Команда /start — убираем дублирование, сразу отправляем пост 1
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    content = load_content()
    step_data = content["post_1"] # Сразу переходим к первому посту лекции
    await message.answer(
        text=step_data["text"],
        reply_markup=get_keyboard(step_data),
        disable_web_page_preview=True
    )

# Команда /analytics — выдает ссылку на канал
@dp.message(Command("analytics"))
async def cmd_analytics(message: types.Message):
    await message.answer(
        text="📊 Access our daily analytics channel here:\n👉 https://t.me/your_channel_link",
        disable_web_page_preview=True
    )

# Команда /help из меню команд
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    content = load_content()
    step_data = content["sys_help"]
    await message.answer(text=step_data["text"], reply_markup=get_keyboard(step_data))

# Команда /support из меню команд
@dp.message(Command("support"))
async def cmd_support(message: types.Message):
    content = load_content()
    step_data = content["sys_support"]
    await message.answer(text=step_data["text"], reply_markup=get_keyboard(step_data))

# Хэндлер переходов по шагам обучения (новые посты добавляются в ленту)
@dp.callback_query(F.data.startswith("step:"))
async def handle_steps(callback: types.CallbackQuery):
    step_name = callback.data.split(":")[1]
    content = load_content()
    
    if step_name in content:
        step_data = content[step_name]
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
        await callback.message.answer(
            text=step_data["text"],
            reply_markup=get_keyboard(step_data)
        )
    await callback.answer()

async def main():
    # Настройка нативного меню команд на английском языке
    commands = [
        types.BotCommand(command="start", description="Start learning process"),
        types.BotCommand(command="analytics", description="Daily analytics channel"),
        types.BotCommand(command="help", description="Help & Information"),
        types.BotCommand(command="support", description="Contact support")
    ]
    await bot.set_my_commands(commands)

    # Автоматическая настройка текста описания до старта бота
    try:
        content = load_content()
        description_text = content["pre_start"]["text"]
        await bot.set_my_description(description=description_text)
    except Exception as e:
        logging.error(f"Не удалось установить описание бота: {e}")

    print("Робот Tick Tape запущен и готов к размотке графиков...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
