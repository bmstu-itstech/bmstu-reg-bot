from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from services.exc import NotRegistered, TooManyTeammates
from services.service import service
from .keyboards import agreement_kb, university_kb, register_kb, create_profile_kb, confirm_kb
from .states import Registration, TeamFSM


router = Router()


@router.message(commands=['start'])
async def start_handler(msg: Message, state: FSMContext):
    user_id = msg.from_user.id

    profile = await service.get_profile(user_id)

    if not profile:
        await msg.answer(
            'Добро пожаловать в бота!',
            reply_markup=register_kb
        )
    else:
        team = await service.get_participant_team(user_id)
        main_kb = create_profile_kb(True if team else False)

        await msg.answer(
            'Рады вас видеть снова)',
            reply_markup=main_kb
        )

    profile = await service.get_profile(user_id)
    if not profile:
        await msg.answer('Для продолжения нужна регистрация. Давайте начнем.')
        await state.set_state(Registration.agreement)


@router.message(F.text == 'Профиль')
async def display_profile(msg: Message):
    participant = await service.get_profile(msg.from_user.id)
    if not participant:
        await msg.answer(
            'Вы не зарегистрированы',
            reply_markup=register_kb
        )
        return

    team = await service.get_participant_team(msg.from_user.id)
    await msg.answer(
        'Ваш профиль\n\n'
        f'ФИО: {participant.last_name} {participant.first_name} {participant.middle_name}\n'
        f'ВУЗ: {participant.university}\n'
        f'Команда: {team.name if team else 'не участвувете'}',
        reply_markup=create_profile_kb(has_team=(team is not None))
    )