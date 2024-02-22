import re

from aiogram import F, types, Router
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.MESSAGES import MESSAGES
from bot.handlers.helpers import add_days_to_today, file_processing
from bot.handlers.start import bot_start
from bot.keyboards.main import start_btns, main_menu_btn, executors_inline_btns
from bot.loader import dp, bot, form_router
from bot.models import EEUser, Task
from bot.state.product import TaskCreateState, TaskCompleteState


@form_router.message(F.text == '📌 Создать поручение')
async def create_task_step(message: types.Message, state: FSMContext):
    keyboard = main_menu_btn()
    await bot.send_message(message.from_user.id,
                           MESSAGES['task_title'],
                           reply_markup=keyboard)
    await state.set_state(TaskCreateState.title)


@form_router.message(TaskCreateState.title)
async def task_title_step(message: types.Message, state: FSMContext):
    file_data = file_processing(message)
    executors = EEUser.objects.exclude(tg_id=message.from_user.id)
    markup = executors_inline_btns(executors)
    creator = EEUser.objects.get(tg_id=message.from_user.id)
    task = Task.objects.create(title=file_data['title'], creator=creator,
                               file_id=file_data['file_id'],
                               file_type=file_data['file_type'])
    await state.update_data(task_id=task.pk)
    await bot.send_message(message.from_user.id,
                           MESSAGES['task_created'].format(task.pk), reply_markup=markup)
    await state.set_state(TaskCreateState.executor)


@form_router.callback_query(TaskCreateState.executor, F.data.startswith("executor_"))
async def task_choose_executor_step(callback_query: types.CallbackQuery, state: FSMContext):
    _, executor_id = callback_query.data.split('_')
    await state.update_data(executor_id=executor_id)
    await bot.edit_message_text(MESSAGES['period_of_execution'], callback_query.from_user.id,
                                callback_query.message.message_id, reply_markup=None)
    await state.set_state(TaskCreateState.period)


@form_router.message(TaskCreateState.period)
async def period_of_execution_step(message: types.Message, state: FSMContext):
    period = message.text
    if re.match(r'^\d+$', period):
        data = await state.get_data()
        result_date = add_days_to_today(period)
        task = Task.objects.get(id=data['task_id'])
        task.executor_id = data['executor_id']
        task.finish_date = result_date
        task.status = 'progress'
        task.save()
        executor = EEUser.objects.get(id=data['executor_id'])
        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(
                text='✅Выполнено',
                callback_data=f'complete-task_{task.pk}'),
        )

        if task.file_id:
            match task.file_type:
                case 'photo':
                    await bot.send_photo(executor.tg_id, task.file_id, caption='📎 Прикреплённый файл')
                case 'document':
                    await bot.send_document(executor.tg_id, task.file_id, caption='📎 Прикреплённый файл')
        await bot.send_message(executor.tg_id, MESSAGES['executor_task']
                               .format(id=task.pk, creator=task.creator.fullname, title=task.title,
                                       status=task.get_status_display(), finish_date=task.finish_date),
                               reply_markup=builder.as_markup())
        keyboard = main_menu_btn()
        await bot.send_message(message.from_user.id, MESSAGES['task_sent'], reply_markup=keyboard)
        await state.clear()
    else:
        await message.answer("Пожалуйста, введите только цифры.")


@form_router.callback_query(F.data.startswith('complete-task_'))
async def complete_task_step(callback_query: types.CallbackQuery, state: FSMContext):
    _, task_id = callback_query.data.split('_')
    await callback_query.message.answer(MESSAGES['complete_task'])
    # Task.objects.filter(task_id=task_id).update(message_id=callback_query.message.message_id)
    await state.update_data(task_id=task_id, message_id=callback_query.message.message_id)
    await state.set_state(TaskCompleteState.result_title)


@form_router.message(TaskCompleteState.result_title)
async def task_complete_title_step(message: types.Message, state: FSMContext):
    data = await state.get_data()
    file_data = file_processing(message)
    task = Task.objects.get(id=data['task_id'])
    task.result = file_data['title']
    task.result_file_id = file_data['file_id']
    task.status = 'completed'
    task.save()
    # Task.objects.filter(id=data['task_id']).update(result=file_data['title'], result_file_id=file_data['file_id'])
    keyboard = main_menu_btn()
    await bot.send_message(message.from_user.id, MESSAGES['task_sent'], reply_markup=keyboard)
    message_text = MESSAGES['executor_task'].format(id=task.pk, creator=task.creator.fullname,
                                                    title=task.title,
                                                    status=task.get_status_display(),
                                                    finish_date=task.finish_date)
    await bot.edit_message_text(message_text, message.from_user.id, int(data['message_id']), reply_markup=None)
