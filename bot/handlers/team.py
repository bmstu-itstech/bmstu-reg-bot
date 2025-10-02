from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from services.exc import NotRegistered, TooManyTeammates, AlreadyExists
from services.service import service
from .keyboards import agreement_kb, university_kb, register_kb, create_profile_kb, confirm_kb
from .states import Registration, Team


router = Router()


@router.message(F.text == 'Команда')
async def display_my_team(msg: Message):
    user_id = msg.from_user.id
    try:
        team = await service.get_participant_team(user_id)

        if not team:
            msg.answer(
                'Вашей команды не сущетсвует',
                reply_markup=create_profile_kb(has_team=False)
            )
        
        members_id = [
            await service.get_username_by_id(id)
            for id in team.participant_ids
        ]

        members_str = '\n'.join([name for name in members_id if name])

        await msg.answer(
            'Твоя команда:\n'
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
    await service.remove_teammate(team.name)

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

    state.set_state(Team.name)
    msg.answer(
        'Введите имя команды'
    )


@router.message(F.text, Team.name)
async def enter_team_name(msg: Message, state: FSMContext):
    team_name = msg.text
    
    if len(team_name.split(' ')) > 1:
        msg.answer(
            'Пробелы в названии недопустимы, введите другое имя',
        )
        state.set_state(Team.name)
        return
    
    user_id = msg.from_user.id
    
    try:
        team = await service.create_team(team_name)
        await service.add_teammate(team.name, msg.from_user.id)
    except AlreadyExists:
        msg.answer(
            'Команда с таким названием уже есть\n\n Введите другое'
        )
        state.set_state(Team.name)
        return
    except Exception:
        await msg.answer(
            'Произошла ошибка, попробуйте еще раз',
            reply_markup=create_profile_kb(has_team=False)
        )