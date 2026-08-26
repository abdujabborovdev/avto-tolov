from aiogram.fsm.state import State, StatesGroup


class Send_m(StatesGroup):
    mess = State()