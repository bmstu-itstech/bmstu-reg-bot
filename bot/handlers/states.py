from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    agreement = State()
    fio = State()
    university = State()
    other_university = State()
    group = State()
    passport = State()
    confirm = State()

class TeamFSM(StatesGroup):
    name = State()
    join_code = State()