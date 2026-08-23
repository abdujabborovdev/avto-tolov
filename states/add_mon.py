from aiogram.fsm.state import State, StatesGroup

class Suma_qosh(StatesGroup):
    tg_idsi = State()
    summa = State()


class AdminSearchState(StatesGroup):
  waiting_for_user_id = State()
