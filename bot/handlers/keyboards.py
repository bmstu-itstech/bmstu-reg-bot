from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

agreement_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Согласен", callback_data="agree")]
    ]
)

university_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data='bmstu')],
        [InlineKeyboardButton(text='Нет', callback_data='other_university')]
    ]
)

register_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Зарегистрироваться')]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

confirm_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Да', callback_data='confirmed'), 
            InlineKeyboardButton(text='Нет', callback_data='not_confirmed')
        ]
    ]
)


def create_profile_kb(has_team: bool):
    if has_team:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='Профиль')],
                [KeyboardButton(text='Покинуть команду'), KeyboardButton(text='Команда')]
            ],
            resize_keyboard=True
        )
    
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Профиль')],
            [KeyboardButton(text='Создать команду'), KeyboardButton(text='Удалить команду')]
        ],
        resize_keyboard=True
    )