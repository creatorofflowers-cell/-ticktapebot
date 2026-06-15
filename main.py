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

# Команда /start — показывает Pre-Start пост (дескриптор)
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    content = load_content()
    step_data = content["pre_start"]
    await message.answer(
        text=step_data["text"],
        reply_markup=get_keyboard(step_data)
    )

# Обработка системных команд /help и /support через текстовый ввод
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    content = load_content()
    step_data = content["sys_help"]
    await message.answer(text=step_data["text"], reply_markup=get_keyboard(step_data))

@dp.message(Command("support"))
async def cmd_support(message: types.Message):
    content = load_content()
    step_data = content["sys_support"]
    await message.answer(text=step_data["text"], reply_markup=get_keyboard(step_data))

# Хэндлер переходов по шагам обучения
@dp.callback_query(F.data.startswith("step:"))
async def handle_steps(callback: types.CallbackQuery):
    step_name = callback.data.split(":")[1]
    content = load_content()
    
    if step_name in content:
        step_data = content[step_name]
        await callback.message.edit_text(
            text=step_data["text"],
            reply_markup=get_keyboard(step_data),
            disable_web_page_preview=True
        )
    await callback.answer()

# Хэндлер для доп. разделов (Help / Support) через кнопки
@dp.callback_query(F.data.startswith("sys:"))
async def handle_sys_steps(callback: types.CallbackQuery):
    sys_action = callback.data.split(":")[1]
    content = load_content()
    key = f"sys_{sys_action}"
    
    if key in content:
        step_data = content[key]
        await callback.message.edit_text(
            text=step_data["text"],
            reply_markup=get_keyboard(step_data)
        )
    await callback.answer()

async def main():
    print("Робот Tick Tape запущен и готов к размотке графиков...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
