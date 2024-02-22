from aiogram import F, types, Router
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup, InputFile, \
    FSInputFile, URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.core.files.base import ContentFile

from bot.MESSAGES import MESSAGES
from bot.handlers.start import bot_start
from bot.keyboards.main import pre_send_btns, start_btns, inline_btns
from bot.loader import dp, bot, form_router
from client.models import Client, Application
from product.models import ProductCategory, Product, ProductOption, ProductType
from bot.state.product import ApplicationState
from service.models import Service


@form_router.message(F.text.in_([MESSAGES['btn_product_ru'], MESSAGES['btn_product_uz'], MESSAGES['btn_product_kr']]))
async def product_category_step(message: types.Message, state: FSMContext):
    client = Client.objects.get(tg_id=message.from_user.id)
    categories = ProductCategory.objects.all()
    markup = inline_btns(categories, client.language, 'product-category_')
    await bot.send_message(message.from_user.id,
                           MESSAGES['choose_category'],
                           reply_markup=markup)
    await state.set_state(ApplicationState.product_type)


@form_router.callback_query(ApplicationState.product_type, F.data.startswith("product-category_"))
async def product_type_choose_step(callback_query: types.CallbackQuery, state: FSMContext):
    _, category_id = callback_query.data.split('_')
    client = Client.objects.get(tg_id=callback_query.from_user.id)
    category = ProductCategory.objects.get(id=category_id)
    if category.is_show_type:
        product_types = ProductType.objects.all()
        await state.update_data(category_id=category_id)
        markup = inline_btns(product_types, client.language, 'product-type_')
        await callback_query.message.answer(MESSAGES['choose_interest'], reply_markup=markup)
        await state.set_state(ApplicationState.interest)
    else:
        products = Product.objects.filter(category_id=category_id)
        markup = inline_btns(products, client.language, 'interest_product_')
        await callback_query.message.answer(MESSAGES['choose_interest'], reply_markup=markup)
        await state.set_state(ApplicationState.check_phone)


@form_router.callback_query(ApplicationState.interest, F.data.startswith("product-type_"))
async def category_detail_step(callback_query: types.CallbackQuery, state: FSMContext):
    _, product_type_id = callback_query.data.split('_')
    await state.update_data(product_type_id=product_type_id)
    data = await state.get_data()
    client = Client.objects.get(tg_id=callback_query.from_user.id)
    products = Product.objects.filter(category_id=data['category_id'], product_type_id=product_type_id)
    markup = inline_btns(products, client.language, 'interest_product_')
    await callback_query.message.answer(MESSAGES['choose_interest'], reply_markup=markup)
    await state.set_state(ApplicationState.check_phone)


@form_router.callback_query(ApplicationState.check_phone, F.data.startswith("interest_"))
async def check_phone_step(callback_query: types.CallbackQuery, state: FSMContext):
    _, action, model_id = callback_query.data.split('_')
    await state.update_data(model_id=model_id, model_type=action)
    client = Client.objects.get(tg_id=callback_query.from_user.id)
    if client.phone:
        if action == 'product':
            await state.set_state(ApplicationState.product_option)
            await product_option_step(callback_query, state)
        else:
            await state.set_state(ApplicationState.application_service)
            await service_application_detail_step(callback_query, state)
    else:
        await state.set_state(ApplicationState.pre_send)
        await add_phone_step(callback_query, state)


async def get_model(action, model_id):
    model = Product
    if action == 'service':
        model = Service
    model = model.objects.get(id=model_id)
    return model


@form_router.callback_query(ApplicationState.product_option)
async def product_option_step(callback_query: types.CallbackQuery, state: FSMContext):
    client = Client.objects.get(tg_id=callback_query.from_user.id)
    data = await state.get_data()
    product_options = ProductOption.objects.filter(product_id=data['model_id'])
    builder = InlineKeyboardBuilder()
    for obj in product_options:
        builder.row(
            types.InlineKeyboardButton(
                text=f'{obj.power} кВт',
                callback_data=f'product-price_{obj.pk}')
        )
    builder.row(
        types.InlineKeyboardButton(
            text='Другое',
            callback_data='write_kilowatt'
        )
    )
    await callback_query.message.answer(MESSAGES['choose_product'], reply_markup=builder.as_markup())
    await state.set_state(ApplicationState.application_product)


@form_router.callback_query(ApplicationState.application_product, F.data.startswith('product-price_'))
async def product_application_detail_step(callback_query: types.CallbackQuery, state: FSMContext):
    _, model_id = callback_query.data.split('_')
    kb = await pre_send_btns()
    client = Client.objects.get(tg_id=callback_query.from_user.id)
    await state.update_data(comment='-')
    data = await state.get_data()
    product_option = ProductOption.objects.get(id=model_id)
    print(product_option.photo.path)
    # with open('media/photos/setevoy_8pKxvOE.jpg', 'rb') as photo_file:
    await bot.send_photo(callback_query.from_user.id, photo=FSInputFile(
            path=product_option.photo.path,
        ), caption=product_option.product.get_description_by_lang(client.language))
    await state.update_data(kilowatt=product_option.power)
    model = await get_model(data['model_type'], data['model_id'])
    messages = (f'Категория: {model.category.get_name_by_lang(client.language)}\n'
                f'Продукт: {model.get_name_by_lang(client.language)}\n'
                f'Мощность: {product_option.power} кВт\n'
                f'Клиент: {client.fullname}\n'
                f'Номер телефона: {client.phone}\n'
                f'Комментарий: {data["comment"]}\n\n')
    await callback_query.message.answer(
        messages,
        reply_markup=kb)
    await state.set_state(ApplicationState.pre_send)


@form_router.callback_query(ApplicationState.application_product, F.data.startswith('write_kilowatt'))
async def write_kilowatt_step(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer(
        MESSAGES['write_kilowatt'])
    await state.set_state(ApplicationState.write_kilowatt)


@form_router.message(ApplicationState.write_kilowatt)
async def product_application_detail_step_kilowatt(message: types.Message, state: FSMContext):
    await state.update_data(kilowatt=message.text)
    kb = await pre_send_btns()
    client = Client.objects.get(tg_id=message.from_user.id)
    await state.update_data(comment='-')
    data = await state.get_data()
    model = await get_model(data['model_type'], data['model_id'])
    messages = (f'Категория: {model.category.get_name_by_lang(client.language)}\n'
                f'Продукт: {model.get_name_by_lang(client.language)}\n'
                f'Мощность: {data["kilowatt"]} кВт\n'
                f'Клиент: {client.fullname}\n'
                f'Номер телефона: {client.phone}\n'
                f'Комментарий: {data["comment"]}\n\n')
    await message.answer(
        messages,
        reply_markup=kb)


@form_router.callback_query(ApplicationState.application_service)
async def service_application_detail_step(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(comment='-')
    kb = await pre_send_btns()
    client = Client.objects.get(tg_id=callback_query.from_user.id)
    data = await state.get_data()
    model = await get_model(data['model_type'], data['model_id'])
    messages = (f'Услуга: {model.get_name_by_lang(client.language)}\n'
                f'Клиент: {client.fullname}\n'
                f'Номер телефона: {client.phone}\n'
                f'Комментарий: {data["comment"]}\n\n')
    await callback_query.message.answer(messages, reply_markup=kb)
    await state.set_state(ApplicationState.pre_send)


@form_router.callback_query(ApplicationState.pre_send, F.data == 'update_comment')
async def add_comment_step(callback_query: types.CallbackQuery, state: FSMContext):
    new_msg = await callback_query.message.answer(MESSAGES['update_comment'],
                                                  reply_markup=ReplyKeyboardRemove())
    await state.update_data(message_id=callback_query.message.message_id,
                            message_id_for_delete=new_msg.message_id)
    await state.set_state(ApplicationState.comment)


@form_router.callback_query(ApplicationState.pre_send, F.data == 'update_phone')
async def add_phone_step(callback_query: types.CallbackQuery, state: FSMContext):
    kb = [
        [
            KeyboardButton(text="Отправить контакты 📞", request_contact=True),

        ]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    new_msg = await callback_query.message.answer(MESSAGES['update_phone'],
                                                  reply_markup=keyboard)
    await state.update_data(message_id=callback_query.message.message_id,
                            message_id_for_delete=new_msg.message_id)
    await state.set_state(ApplicationState.phone)


async def update_pre_send(message, data, model, client):
    kb = await pre_send_btns()
    await bot.delete_message(message.from_user.id, message.message_id)
    await bot.delete_message(message.from_user.id, data['message_id_for_delete'])
    try:
        await bot.edit_message_text(MESSAGES['model_detail'].format(model=model,
                                                                    client=client,
                                                                    comment=data['comment']),
                                    message.from_user.id,
                                    data['message_id'],
                                    reply_markup=kb)
    except Exception as err:
        print(err)


@form_router.message(ApplicationState.comment)
async def update_comment_step(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    model = await get_model(data['model_type'], data['model_id'])
    client = Client.objects.get(tg_id=message.from_user.id)
    await update_pre_send(message, data, model, client)
    await state.set_state(ApplicationState.pre_send)


@form_router.message(ApplicationState.phone)
async def update_phone_step(message: types.Message, state: FSMContext):
    phone = message.text
    if message.contact:
        phone = message.contact.phone_number
    await state.update_data(phone=phone)
    data = await state.get_data()
    model = await get_model(data['model_type'], data['model_id'])
    client = Client.objects.get(tg_id=message.from_user.id)
    client.phone = data['phone']
    await update_pre_send(message, data, model, client)
    client.save()
    await state.set_state(ApplicationState.pre_send)


@form_router.callback_query(F.data == 'send_application')
async def send_application(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    client = Client.objects.get(tg_id=callback_query.from_user.id)
    qs_dict = {}
    if data['model_type'] == 'product':
        qs_dict['product_id'] = data['model_id']
    else:
        qs_dict['service_id'] = data['model_id']
    if data.get('kilowatt'):
        qs_dict['kilowatt'] = data['kilowatt']
    Application.objects.create(client=client, comment=data['comment'], **qs_dict)
    keyboard = start_btns(client.language)
    await callback_query.message.answer(MESSAGES['send_application'], reply_markup=keyboard)
    await callback_query.message.delete_reply_markup()
    await state.clear()


@form_router.callback_query(F.data == 'cancel_application')
async def cancel_application(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    client = Client.objects.get(tg_id=callback_query.from_user.id)
    keyboard = start_btns(client.language)
    await callback_query.message.answer(MESSAGES['cancel_application'], reply_markup=keyboard)
    await callback_query.message.delete_reply_markup()
