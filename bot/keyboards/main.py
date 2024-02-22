# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
#
# from bot.models import CategoryProduct, LocationPoint, Product
#
# TG_BUTTON_MAX_LENGTH = 28
#
#
# async def generate_keyboard(btns, **kwargs):
#     reply_kb = ReplyKeyboardMarkup(**kwargs)
#     for desc in btns:
#         if desc:
#             reply_kb.insert(desc[:TG_BUTTON_MAX_LENGTH])
#     return reply_kb
#
#
# async def generate_keyboard_inline(*args, **kwargs):
#     kb = InlineKeyboardMarkup(**kwargs)
#     if isinstance(*args, list):
#         for arg in args:
#             for btn in arg:
#                 kb.insert(btn)
#     else:
#         kb.insert(*args)
#     return kb
#
#
# async def show_categories():
#     categories = CategoryProduct.objects.values_list('id', 'title')
#     btns = []
#     for obj_id, title in categories:
#         btn = InlineKeyboardButton(title, callback_data=f'category_{obj_id}')
#         btns.append(btn)
#     categories_kb = await generate_keyboard_inline(btns, row_width=1)
#     return categories_kb
#
#
# async def show_products(category_id):
#     products = Product.objects.filter(category_id=category_id).values_list('id', 'title')
#     btns = []
#     for obj_id, title in products:
#         btn = InlineKeyboardButton(title, callback_data=f'product_{obj_id}')
#         btns.append(btn)
#     products_kb = await generate_keyboard_inline(btns, row_width=2)
#     return products_kb
#
#
# async def show_location_points():
#     locations = LocationPoint.objects.values_list('id', 'title')
#     btns = []
#     for obj_id, title in locations:
#         btn = InlineKeyboardButton(f'{title}🟢', callback_data=f'location_{obj_id}')
#         btns.append(btn)
#     locations_kb = await generate_keyboard_inline(btns, row_width=2)
#     return locations_kb
#
#
# async def show_question_btn(order):
#     question_btn = [InlineKeyboardButton('✅ Принять',
#                                          callback_data=f'accept_order|{order.id}'),
#                     InlineKeyboardButton('❌ Отменить', callback_data=f'cancel_order|{order.id}')]
#     question_kb = await generate_keyboard_inline(question_btn)
#     return question_kb
from aiogram import types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.MESSAGES import MESSAGES


async def pre_send_btns():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text='Изменить номер телефона📞',
            callback_data=f'update_phone'),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='Изменить комментарий📝',
            callback_data=f'update_comment'),
    )
    builder.row(
        types.InlineKeyboardButton(
            text='Отменить заявку❌',
            callback_data='cancel_application'),
        types.InlineKeyboardButton(
            text='Отправить заявку✅',
            callback_data='send_application')

    )

    return builder.as_markup()


def main_menu_btn():
    kb = [
        [
            KeyboardButton(text='🔙 Главное меню'),
        ],

    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard


def start_btns():
    kb = [
        [
            KeyboardButton(text='🛒 Создать лот'),
            KeyboardButton(text='📌 Создать поручение'),
        ],
        [
            KeyboardButton(text='📃 Статусы по лотам'),
            KeyboardButton(text='📃 Статусы поручений'),
        ],
        [
            KeyboardButton(text='🔎 Поиск по лотам'),
            KeyboardButton(text='🔎 Поиск поручений'),
        ],

    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                   input_field_placeholder="Выберите что вас именно интересует 👇🏼")
    return keyboard


def phone_btns():
    kb = [
        [
            KeyboardButton(text="📱 Поделиться номером телефона", request_contact=True),
        ],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True,
                                   input_field_placeholder="Поделитесь своим контактом для авторизации 👇🏼")
    return keyboard


def executors_inline_btns(qs):
    builder = InlineKeyboardBuilder()
    for obj in qs:
        builder.row(
            types.InlineKeyboardButton(
                text=f'{obj.fullname}',
                callback_data=f'executor_{obj.pk}')
        )
    return builder.as_markup()
