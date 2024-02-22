from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.MESSAGES import MESSAGES
from bot.loader import form_router, bot, dp


@form_router.message(F.text.in_([MESSAGES['btn_contact_ru'], MESSAGES['btn_contact_uz'], MESSAGES['btn_contact_kr']]))
async def product_category_step(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id,
                           MESSAGES['contact'],
                           parse_mode='HTML')


@form_router.message(F.text.in_([MESSAGES['btn_about_us_ru'], MESSAGES['btn_about_us_uz'], MESSAGES['btn_about_us_kr']]))
async def product_category_step(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id,
                           MESSAGES['about_us'])
