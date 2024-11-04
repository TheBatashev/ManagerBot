from aiogram.fsm.state import StatesGroup, State

class UserState(StatesGroup):
    captcha = State()