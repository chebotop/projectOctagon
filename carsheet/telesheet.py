import gspread
from oauth2client.service_account import ServiceAccountCredentials
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()
creds = ServiceAccountCredentials.from_json_keyfile_name('carsheet\data\secret_key.json')
scopes=[os.getenv('SCOPE_SHEETS'), os.getenv('SCOPE_DRIVE')]


def fetch_data_from_gsheets():
    return gspread.authorize(creds).open('Cars and tip').sheet1


def is_number_exist(keyword):
    data = fetch_data_from_gsheets().get_all_values()
    respond = [' '.join(sublist) for sublist in data if keyword.lower() in sublist[0].lower()]
    return '\n'.join(respond) if respond else False


def add_new_data(data):
    fetch_data_from_gsheets().append_row(data.split(' '))


def choice_keyboard():
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton("1. Сохранить ответ", callback_data="save_response")
    item2 = InlineKeyboardButton("2. Продолжить", callback_data="continue")
    markup.add(item1, item2)
    return markup


TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
    awaiting_additional_data = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Hey, it's a database of cars and tips. Enter the numberplate or model name of a car")


@dp.message_handler(content_types=types.ContentType.TEXT)
async def process_message(message: types.Message, state: FSMContext):
    text = message.text
    current_state = await state.get_state()
    try:
        if current_state != 'Form:awaiting_additional_data':
            num = is_number_exist(text)
            if not num:
                markup = choice_keyboard()
                await message.answer(f"Have you the full data for add data {text} to sheets?", reply_markup=markup)
                await state.update_data(numberplate=text)
                await Form.awaiting_additional_data.set()
                await message.answer(f"Enter additional data for car #{text} in format: 'model tip'")
            elif text.split(' ')[0].isdigit() and text.split(' ')[2].isdigit():
                add_new_data(text)
                await message.answer(f'Car #{text} added')
    except IndexError:
        await message.answer(num)

#добавление комбинированных данных
@dp.message_handler(state=Form.awaiting_additional_data, content_types=types.ContentType.TEXT)
async def process_input_data(message: types.Message, state: FSMContext):
    combined_data = f"{(await state.get_data()).get('numberplate')} {message.text}"
    add_new_data(combined_data)
    await message.answer(f'Car #{combined_data} added')
    await state.reset_state()

@dp.callback_query_handler(lambda c: c.data == "save_response", state=Form.awaiting_additional_data)
async def save_response(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    # Сохраните ответ пользователя, например:
    user_data = await state.get_data()
    numberplates = {}
    numberplates[user_data.get("numberplate")] = "empty value"
    # Тут добавьте ваш код для сохранения ответа
    await callback_query.message.answer(f"You've chosen to save the response for car {numberplate}.")
    await state.reset_state()
    print(numberplate)

@dp.callback_query_handler(lambda c: c.data == "continue", state=Form.awaiting_additional_data)
async def continue_without_saving(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer("Please, enter the additional data in format: 'model tip'.")


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp)
