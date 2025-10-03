from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

agreement_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Согласен")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

university_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Да')],
        [KeyboardButton(text='Нет')]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

register_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Зарегистрироваться')]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

confirm_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Да'),
            KeyboardButton(text='Нет')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


def create_profile_kb(has_team: bool):
    if has_team:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='Профиль')],
                [KeyboardButton(text='Покинуть команду')]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Профиль')],
            [KeyboardButton(text='Вступить в команду')],
            [KeyboardButton(text='Создать команду')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )