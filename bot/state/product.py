from aiogram.fsm.state import StatesGroup, State


class TaskCreateState(StatesGroup):
    title = State()
    executor = State()
    period = State()


class TaskCompleteState(StatesGroup):
    result_title = State()
