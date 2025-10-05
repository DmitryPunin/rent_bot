import aiogram
import asyncio
from database import db
from adodbapi import DatabaseError
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from config import token
from datetime import *
from states import Form, select
from aiogram import F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery


token = token
bot = aiogram.Bot(token)

dp = aiogram.Dispatcher()


@dp.message(Command('start'))
async def start(message:Message):
    solution = ''
    if datetime.now().time().hour >= 17:
        solution = 'Добрый вечер!'
    elif 12 <= datetime.now().hour < 17:
        solution = 'Добрый день!'
    elif 4 >= datetime.now().hour <= 11:
        solution = 'Доброе утро!'
    btn_publish_offer = InlineKeyboardButton(text='📢Выложить обьявление',callback_data='publish_offer')
    btn_find_housing = InlineKeyboardButton(text='🔎Найти жилье',callback_data='find_housing')

    m = InlineKeyboardMarkup(inline_keyboard=[[btn_find_housing],[btn_publish_offer]])
    await bot.send_message(message.chat.id,
                           f'{solution} 🔎 Это бот для поиска жилья. Здесь вы также можете разместить своё объявление о посуточной аренде жилья."',reply_markup=m)
@dp.callback_query(F.data == 'find_housing')
async def find_rent(call:CallbackQuery,state:FSMContext):

    await bot.send_message(call.message.chat.id, 'Пожалуйста, введите тип жилья для аренды.Примеры:\n🏠 Квартира\n🏡 Дом  \n🚪 Комната\n🏙️ Апартаменты')
    await state.set_state(select.type)
    await call.answer()

@dp.message(select.type)
async def process_city(message:Message, state: FSMContext):
    await state.update_data(select_type=message.text)
    await bot.send_message(message.chat.id,'Укажите город, в котором вы хотите снять жилье')
    await state.set_state(select.city)

@dp.message(select.city)
async def process_city(message:Message, state: FSMContext):
    await state.update_data(select_city=message.text)
    await bot.send_message(message.chat.id,'На какой улице вы ищете жилье? 🗺️\nЕсли этот параметр не важен, просто напишите "пропустить".')
    await state.set_state(select.street)

@dp.message(select.street)
async def process_city(message:Message, state: FSMContext):
    if message.text.lower() != 'пропустить':
        await state.update_data(select_street=message.text)
    else:
        await state.update_data(select_street='')
    await bot.send_message(message.chat.id,
                           '💰 Укажите бюджет аренды за сутки:\n\nВведите диапазон цен в рублях.\nНапример: 1500-3000')
    await state.set_state(select.price_range)
@dp.message(select.price_range)
async def finally_step(message:Message, state:FSMContext):
    try:
        user_data_ = await state.get_data()
        price_range = message.text
        select_street = user_data_.get('select_street')
        select_type = user_data_.get('select_type')
        select_city = user_data_.get('select_city')
        from_price = price_range.split('-')[0]
        to_price = price_range.split('-')[1]

        if not select_type or not select_city:
            await message.answer('❌Ошибка: не все данные получены. Попробуйте снова.')
            await state.clear()
            return


        result = db.select_rent(select_type,select_city,from_price,to_price,select_street)

        if not result:
            await message.answer('❌По вашему запросу ничего не найдено.')
        else:

            for offer in result:

                await message.answer(
                    f'✅Найдено предложение!\n'
                    f'🏡Тип: {offer[0]}\n'
                    f'🏙Город: {offer[1]}\n'
                    f'💸Цена: {offer[2]} руб./сутки\n'
                    f'🏠Улица: {offer[3]}\n'
                    f'📞Контакт продавца: {offer[4]}\n\n'

                )


        await state.clear()

    except ValueError:
        await message.answer('❌Произошла ошибка, попробуйте позже')
    except DatabaseError:
        await message.answer('❌Произошла ошибка, попробуйте позже')


@dp.callback_query(F.data == 'publish_offer')
async def find_client(call: CallbackQuery, state: FSMContext):
    await bot.send_message(call.message.chat.id,'🏡 Какой тип жилья вы сдаете?\n\nНапример:\nКвартира\nДом\nКомната\nАпартаменты\nСтудия')
    await state.set_state(Form.type)
    await call.answer()


@dp.message(Form.type)
async def process_type(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    await message.answer('🏙 В каком городе находится ваше жилье?')
    await state.set_state(Form.city)



@dp.message(Form.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer('💸Введите цену за сутки проживания в рублях')
    await state.set_state(Form.price)

@dp.message(Form.price)
async def process_street(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer('🏠Укажите улицу, на которой вы сдаете жилье')
    await state.set_state(Form.street)

@dp.message(Form.street)
async def process_contact(message: Message, state: FSMContext):
    await state.update_data(street=message.text)
    await message.answer('📞 Укажите контактные данные для связи с вами')
    await state.set_state(Form.contact)


@dp.message(Form.contact)
async def process_finally(message: Message, state: FSMContext):
    try:
        contact = message.text
        user_data = await state.get_data()
        street = user_data.get('street')
        price = user_data.get('price')
        type = user_data.get('type')
        city = user_data.get('city')

        if not type or not city:
            await message.answer('❌Ошибка: не все данные получены. Попробуйте снова.')
            await state.clear()
            return


        db.insert_rent(type,city,price,street,contact)


        await message.answer(
                f'✅ Отлично! Ваше предложение сохранено:\n'
                f'🏡Тип: {type}\n'
                f'🏙Город: {city}\n'
                f'💸Цена: {price} руб./сутки\n'
                f'🏠Улица: {street}\n'
                f'📞Ваши контакты: {contact}\n\n'
                f'🤵Теперь клиенты смогут найти ваше предложение через'
            )


        await state.clear()

    except ValueError:
        await message.answer('❌Произашла ошибка, попробуйте позже')
    except DatabaseError:
        await message.answer('❌Произашла ошибка, попробуйте позже')


asyncio.run(dp.start_polling(bot))