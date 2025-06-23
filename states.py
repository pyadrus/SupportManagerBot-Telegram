from aiogram.fsm.state import StatesGroup, State

class StartAppealStates(StatesGroup):
    fio = State()
    phone = State()
    question = State()
    edit_type = State() # fio, phone, question
    edit = State() # Измененная информация
