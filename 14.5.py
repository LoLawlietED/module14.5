from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import asyncio
from config import *
import text
from keyboard import *
import logging
from crud_functions import initiate_db, get_all_products, add_user, is_included
from aiogram.dispatcher.filters.state import State, StatesGroup

logging.basicConfig(level= logging.INFO)
bot = Bot(token = api)
dp = Dispatcher(bot, storage = MemoryStorage())

initiate_db()
class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()

@dp.message_handler(text = 'Регистрация')
async def sing_up(message):
    await message.answer(text = 'Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()

@dp.message_handler(state = RegistrationState.username)
async def set_username(message,state):
    username = message.text
    if is_included(username):
        await message.answer(text = 'Пользователь существует, введите другое имя:')
        return
    await state.update_data(username = username)
    await message.answer(text = 'Введите свой email:')
    await RegistrationState.email.set()

@dp.message_handler(state = RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email = message.text)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()

@dp.message_handler(state = RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age = message.text)
    user_data = await state.get_data()
    username = user_data.get('username')
    email = user_data.get('email')
    age = user_data.get('age')
    add_user(username = username, email = email, age = age)
    await state.finish()
    await message.answer("Регистрация завершена!")

@dp.message_handler(commands= ['start'])
async def start_message(message):
    await message.answer(f'Добро пожаловать, {message.from_user.username}\n' + text.start, reply_markup = kb)

@dp.message_handler(text = 'Рассчитать')
async def main_menu(message):
    await message.answer(text = 'Выберите опцию', reply_markup= ikb)

@dp.callback_query_handler(text = 'formulas')
async def get_formulas(call):
    await call.message.answer(text.formula)
    await call.answer()

@dp.message_handler(text = 'Купить')
async def get_buying_list(message: types.Message):
    products = get_all_products()
    i = 0
    for product in products:
        image_path = f"{i}.png"
        i += 1
        with open(image_path, 'rb') as img:
            *_, title, description, price = product
            caption = f'Название: {title}|\nОписание: {description} |\nЦена:: {price}'
            await message.answer_photo(photo=img, caption= caption)
    await message.answer('Выберете продукт для покупки', reply_markup = ikb_2)

@dp.callback_query_handler(text = 'product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.callback_query_handler(text = 'calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()

@dp.message_handler(state = UserState.age)
async def set_growth(message, state):
    await state.update_data(first = message.text)
    await message.answer("Введите свой рост:")
    await UserState.growth.set()

@dp.message_handler(state = UserState.growth)
async def set_weight(message, state):
    await state.update_data(second = message.text)
    await message.answer("Введите свой вес:")
    await UserState.weight.set()

@dp.message_handler(state = UserState.weight)
async def send_calories(message, state):
    await state.update_data(three = message.text)
    data = await state.get_data()
    calories = 10 * float(data["three"]) + 6.25 * float(data["second"]) - 5 * float(data["first"]) - 161
    await message.answer(f'Ваша норма калорий {calories}')
    await state.finish()

@dp.message_handler()
async def all_message(message):
    await message.answer(text.all)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates = True)