from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from services.exc import NotRegistered, TooManyTeammates, AlreadyExists
from services.service import service
from .keyboards import agreement_kb, university_kb, register_kb, create_profile_kb, confirm_kb
from .states import Registration, Team
from .profile import team_cache

router = Router()

@router.message(F.text == "Зарегистрироваться")
async def start_registration(msg: Message, state: FSMContext):
    await state.set_state(Registration.agreement)
    await msg.answer(
        "Согласие на обработку персональных данных (152-ФЗ)",
        reply_markup=agreement_kb
    )

@router.callback_query(Registration.agreement)
async def agreement_yes(query: CallbackQuery, state: FSMContext):
    await query.message.answer(
        "Введите ФИО через пробелы\n\nПример: Иванов Иван Иванович"
    )
    await state.set_state(Registration.fio)
    await query.answer()


@router.callback_query(Registration.confirm_agreement)
async def agreement_yes(query: CallbackQuery, state: FSMContext):
    callback_data = query.data
    if callback_data == 'agree':
        await query.message.answer(
            'Введите ФИО через пробелы\n\nПример: Иванов Иван Иванович'
        )
        await state.set_state(Registration.fio)
        

@router.message(F.text, Registration.fio)
async def input_fio(msg: Message, state: FSMContext):
    fio = msg.text.split(' ')
    if len(fio) != 3:
        await msg.answer('ФИО заполнено некорректно, попробуйте еще раз')
        await state.set_state(Registration.fio)
        return

    await state.update_data(fio=msg.text)
    await msg.answer(
        'Вы учитесь в Бауманке?',
        reply_markup=university_kb
    )
    await state.set_state(Registration.university)


@router.callback_query(Registration.university)
async def university(query: CallbackQuery, state: FSMContext):
    if query.data == 'bmstu':
        await state.update_data(university='МГТУ им. Баумана')
        await state.set_state(Registration.group)
        await query.message.answer('Введите учебную группу, например РК9-31Б')
    else:
        await state.update_data(university='Other')
        await state.set_state(Registration.other_university)
        await query.message.answer('Введите название ВУЗа')
    

@router.message(F.text, Registration.other_university)
async def other_university(msg: Message, state: FSMContext):
    await state.update_data(university=msg.text)
    await state.set_state(Registration.passport)
    await msg.answer('Напишите серию и номер паспорта: 0000 444888')


async def check_data(msg: Message, state: FSMContext):
    data = await state.get_data()
    university = data.get('university')
    if university == 'МГТУ им. Баумана':
        await msg.answer(
            'Вы подтверждаете введенные данные?\n\n'
            f'ФИО: {data.get('fio')}\n'
            f'Вуз: {data.get('university')}\n'
            f'Группа: {data.get('group')}',
            reply_markup=confirm_kb
        )
    else:
        await msg.answer(
            'Вы подтверждаете введенные данные?\n\n'
            f'ФИО: {data.get('fio')}\n'
            f'Вуз: {data.get('university')}\n'
            f'Паспорт: {data.get('passport')}',
            reply_markup=confirm_kb
        )
    
    await state.set_state(Registration.confirm)


@router.message(Registration.group)
async def input_group(msg: Message, state: FSMContext):
    group = msg.text.split('-')

    if len(group) != 2:
        await msg.answer('Группа введена некорректно. Попробуйте еще раз')
        await state.set_state(Registration.group)
        return

    await state.update_data(group=msg.text)
    await check_data(msg, state)


@router.message(Registration.passport)
async def input_passport(msg: Message, state: FSMContext):
    passport_data = msg.text.split(' ')
    if len(passport_data) != 2:
        msg.answer('Введенные данные некорректны, попробуйте еще раз')
        await state.set_state(Registration.passport)

    passport_data = ''.join(passport_data)

    await state.update_data(passport=passport_data)
    await check_data(msg, state)


@router.callback_query(Registration.confirm)
async def confirm(query: CallbackQuery, state: FSMContext):
    if query.data == 'confirmed':
        try:
            pending_team = team_cache.pop(query.from_user.id, None)
            team_id = await service.get_team_id(pending_team)

            data = await state.get_data()
            fio = data.get('fio').split(' ')
            participant = await service.register_participant(
                user_id=query.from_user.id,
                username=query.from_user.username,
                last_name=fio[0],
                first_name=fio[1],
                middle_name=fio[2],
                university=data.get('university'),
                group=data.get('group'),
                passport=data.get('passport'),
                team_id=team_id
            )
            await query.message.answer(
                'Вы зарегистрированы!',
                reply_markup=create_profile_kb(has_team=False)
            )
        except AlreadyExists:
            await query.message.ansewr(
                'Пользователь с вашим ником уже зарегистрирован',
                reply_markup=register_kb
            )
    else:
        await state.clear()
        await state.set_state()
        await query.message.answer(
            'Регистрация отменена',
            reply_markup=register_kb
        )