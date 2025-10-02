from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    start = State()
    agreement = State()
    confirm_agreement = State()
    fio = State()
    university = State()
    other_university = State()
    group = State()
    passport = State()
    check_data = State()
    confirm = State()

class Team(StatesGroup):
    join = State()
    create = State()