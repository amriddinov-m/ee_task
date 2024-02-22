from aiogram import types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from bot.MESSAGES import MESSAGES

from bot.keyboards.main import start_btns, phone_btns, main_menu_btn
from bot.loader import dp, bot, form_router
from bot.models import EEUser


@dp.message(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    client = EEUser.objects.filter(tg_id=message.from_user.id)
    if client:
        await show_main_btns(message)
    else:
        keyboard = phone_btns()
        await message.answer(MESSAGES['client_start'].format(message.from_user.full_name), reply_markup=keyboard)


@dp.message(F.contact)
async def contact_search_step(message: types.Message):
    phone = message.contact.phone_number
    updated = EEUser.objects.filter(phone=phone).update(tg_id=message.from_user.id)
    if updated:
        keyboard = main_menu_btn()
        await bot.send_message(message.from_user.id,
                               MESSAGES['success_logged'],
                               reply_markup=keyboard)
    else:
        await message.answer(MESSAGES['permission_denied'], reply_markup=None)


@form_router.message(F.text == '🔙 Главное меню')
async def show_main_btns(message: types.Message):
    keyboard = start_btns()
    await bot.send_message(message.from_user.id,
                           MESSAGES['main_step'],
                           reply_markup=keyboard)
