from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.services.exc import NotRegistered, TooManyTeammates, AlreadyExists
from bot.services.service import service
from bot.handlers.keyboards import register_kb, create_profile_kb
from bot.handlers.states import Team
from config import BOT_TELEGRAM_NAME, MAX_TEAMMATES


router = Router()


async def join_team(team_name: str, user_id: int):
    await service.add_teammate(team_name, user_id)


@router.message(F.text == 'Команда')
async def display_my_team(msg: Message):
    user_id = msg.from_user.id
    try:
        team = await service.get_participant_team(user_id)

        if not team:
            await msg.answer(
                'Вашей команды не сущетсвует',
                reply_markup=create_profile_kb(has_team=False)
            )
        
        members_id = [
            await service.get_username_by_id(id)
            for id in team.participant_ids
        ]

        members_str = '\n'.join(['@' + name for name in members_id if name])

        await msg.answer(
            f'Твоя команда ({len(members_id)}/{MAX_TEAMMATES}):\n'
            f'{members_str}'
        )
    except NotRegistered:
        await msg.answer(
            'Вы не зарегистрированы!',
            reply_markup=register_kb
        )
    except Exception as e:
        await msg.answer(
            'Произошла ошибка, попробуйте позже',
            reply_markup=create_profile_kb(has_team=True)
        )


@router.message(F.text == 'Вступить в команду')
async def enter_team_name(msg: Message, state: FSMContext):
    profile = await service.get_profile(msg.from_user.id)

    if not profile:
        await msg.answer(
            'Вы не зарегистрированы',
            reply_markup=register_kb
        )
        return

    await msg.answer(
        'Введите название команды'
    )
    await state.set_state(Team.join)


@router.message(Team.join)
async def join_team(msg: Message, state: FSMContext):
    team_name = msg.text
    if len(team_name.split()) > 1:
        await msg.answer(
            'Некорректное название команды, попробуйте еще раз'
        )
        await state.set_state(Team.join)
        return
    
    try:
        await service.add_teammate(team_name, msg.from_user.id)
        await msg.answer(
            f'Вы вступили в команду {team_name}'
        )
        await state.clear()
    except NotRegistered:
        await msg.answer(
            'Команда не зарегистрирована',
            reply_markup=create_profile_kb(has_team=False)
        )
        await state.clear()
    except TooManyTeammates:
        await msg.answer(
            'Команда заполнена, попробуйте вступить в другую или создать свою',
            reply_markup=create_profile_kb(has_team=False)
        )
        await state.clear()


@router.message(F.text == 'Покинуть команду')
async def leave_team(msg: Message):
    profile = await service.get_profile(msg.from_user.id)
    
    if not profile:
        await msg.answer(
            'Вы не зарегистрированы',
            reply_markup=register_kb
        )
        return
    
    profile_kb = create_profile_kb(has_team=False)

    if not profile.team_id:
        await msg.answer(
            'У вас нет команды',
            reply_markup=profile_kb
        )
        return
    
    team = await service.get_participant_team(profile.user_id)
    await service.remove_teammate(team.name, profile.user_id)

    await msg.answer(
        f'Вы покинули команду {team.name}',
        reply_markup=profile_kb
    )


@router.message(F.text == 'Создать команду')
async def create_team(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    participant = await service.get_profile(user_id)

    if not participant:
        msg.answer(
            'Вы не зарегистрированы',
            reply_markup=register_kb
        )
        return
    
    team = await service.get_participant_team(user_id)
    if team:
        msg.answer(
            'Вы уже находитесь в команде',
            reply_markup=create_profile_kb(has_team=True)
        )

    await state.set_state(Team.create)
    await msg.answer(
        'Введите имя команды'
    )


@router.message(Team.create)
async def enter_team_name(msg: Message, state: FSMContext):
    team_name = msg.text
    
    if len(team_name.split()) > 1:
        await msg.answer(
            'Пробелы в названии недопустимы, введите другое имя',
        )
        await state.set_state(Team.create)
        return
    
    try:
        team = await service.create_team(team_name)
        await service.add_teammate(team.name, msg.from_user.id)
        await msg.answer(
            f'Команда {team.name} создана!'
            f'Ссылка для приглашения: https://t.me/{BOT_TELEGRAM_NAME}?start={team_name}',
            reply_markup=create_profile_kb(has_team=True)
        )
        await state.clear()
    except AlreadyExists:
        await msg.answer(
            'Команда с таким названием уже есть\n\n Введите другое'
        )
        await state.set_state(Team.create)
    except Exception:
        await msg.answer(
            'Произошла ошибка, попробуйте еще раз',
            reply_markup=create_profile_kb(has_team=False)
        )
        await state.clear()