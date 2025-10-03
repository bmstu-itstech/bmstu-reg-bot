from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from bot.handlers.keyboards import register_kb, create_profile_kb
from bot.services.exc import NotRegistered, TooManyTeammates
from bot.services.service import service


router = Router()


team_cache = {}


@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    await msg.answer(
        'Добро пожаловать!'
    )

    params = msg.text.split()
    if len(params) > 1:
        global team_cache
        team_name = params[1]
        team_cache[msg.from_user.id] = team_name
        print(team_cache.get(msg.from_user.id))


    user_id = msg.from_user.id

    profile = await service.get_profile(user_id)

    if not profile:
        await msg.answer(
            'Для продолжения нужна регистрация',
            reply_markup=register_kb
        )
        return
    else:
        team = await service.get_participant_team(user_id)

        await msg.answer(
            'Рады вас видеть снова)',
            reply_markup=create_profile_kb(True if team else False)
        )

    team = await service.get_participant_team(user_id)

    if team:
        await msg.answer(
            f"Вы уже состоите в команде: {team.name}",
            reply_markup=create_profile_kb(True)
        )
    else:
        if team_name:
            try:
                await service.add_teammate(team_name, user_id)
                await msg.answer(
                    f"Вы успешно присоединились к команде {team_name}!",
                    reply_markup=create_profile_kb(True)
                )
            except TooManyTeammates:
                await msg.answer(
                    f'В команде {team_name} слишком много участников\n\n'
                    'Вы можете вступить в другую команду или создать свою'
                )
            except NotRegistered:
                await msg.answer(
                    f'Команды {team_name} не существует\n\n'
                    'Проверьте название, вступите в другую команду или создайте свою'
                )
        else:
            await msg.answer(
                "Рады вас видеть снова!",
                reply_markup=create_profile_kb(False)
            )


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