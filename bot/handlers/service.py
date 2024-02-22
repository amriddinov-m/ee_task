from aiogram import F, types, Router
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.MESSAGES import MESSAGES
from bot.keyboards.main import inline_btns
from bot.loader import dp, bot, form_router
from bot.state.product import ApplicationState
from client.models import Client
from service.models import Service


@form_router.message(F.text.in_([MESSAGES['btn_service_ru'], MESSAGES['btn_service_uz'], MESSAGES['btn_service_kr']]))
async def product_category_step(message: types.Message, state: FSMContext):
    client = Client.objects.get(tg_id=message.from_user.id)
    services = Service.objects.all()
    markup = inline_btns(services, client.language, 'interest_service_')
    await message.answer(MESSAGES['choose_service'], reply_markup=markup)
    await state.set_state(ApplicationState.check_phone)
