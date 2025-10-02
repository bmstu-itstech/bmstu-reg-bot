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

    # if not await service.check_agreement(user_id):
    #     await msg.answer(
    #         'Согласие на обработку ПД (152-ФЗ). Вы согласны?',
    #         reply_markup=agreement_kb
    #     )
    #     return

    profile = await service.get_profile(user_id)
    if not profile:
        await msg.answer('Для продолжения нужна регистрация. Давайте начнем.')
        await state.set_state(Registration.agreement)
    

@router.message(F.text, Registration.agreement)
async def register_handler(msg: Message, state: FSMContext):
    await msg.answer(
        'Согласие на обработку персональных данных (152-ФЗ)',
        reply_markup=agreement_kb
    )
    await state.set_state(Registration.confirm)


@router.message(F.text, Registration.confirm)
async def agreement_yes(msg: Message, state: FSMContext):
    await msg.answer('Введите ФИО через пробелы\n\nПример: Иванов Иван Иванович')
    await state.set_state(Registration.fio)


@router.message(F.text, Registration.fio)
async def input_fio(msg: Message, state: FSMContext):
    fio = msg.text.split(' ')
    if len(fio) != 3:
        await msg.answer('ФИО заполнено некорректно, попробуйте еще раз')
        await state.set_state(Registration.fio)

    await state.update_data(fio=msg.text)
    await msg.answer(
        'Вы учитесь в Бауманке?',
        reply_markup=university_kb
    )
    await state.set_state(Registration.university)


@router.message(F.text, Registration.university)
async def university(query: CallbackQuery, callback_data: str, state: FSMContext):
    if callback_data == 'bmstu':
        await state.update_state(university='МГТУ им. Баумана')
        await query.answer('Введите учебную группу, например РК6-31Б')
        await state.set_state(Registration.group)
    else:
        await state.update_state(university='Other')
        await query.answer('Введите название ВУЗа')
        await state.set_state(Registration.other_university)


@router.message(F.text, Registration.other_university)
async def other_university(msg: Message, state: FSMContext):
    await state.update_state(university=msg.text)
    await state.set_state(Registration.passport)
    await msg.answer('Напишите серию и номер паспорта: 0000 444888')


@router.message(Registration.group)
async def input_group(msg: Message, state: FSMContext):
    group = msg.text.split('-')
    if len(group) != 2:
        await msg.answer('Группа введена некорректно. Попробуйте еще раз')
        await state.set_state(Registration.group)

    await state.update_data(group=msg.text)
    await state.set_state(Registration.confirm)


@router.message(Registration.passport)
async def input_passport(msg: Message, state: FSMContext):
    passport_data = msg.text.split()
    if len(passport_data) != 2:
        msg.answer('Введенные данные некорректны, попробуйте еще раз')
        await state.set_state(Registration.passport)

    passport_data = ''.join(passport_data)

    await state.update_data(passport=passport_data)
    await state.set_state(Registration.confirm)

    data = state.get_data()
    university = data.get('university')
    if university == 'bmstu':
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


@router.message(Registration.confirm)
async def confirm(query: CallbackQuery, callback_data: str, state: FSMContext):
    if callback_data == 'confirmed':
        data = state.get_data()
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
            team_id=None
        )
    else:
        await msg.answer('Регистрация отменена.')
        await state.clear()
        await state.set_state()


# --- Команды ---
@router.message(commands=['create_team'])
async def create_team_start(msg: Message, state: FSMContext):
    await msg.answer('Введите название команды (должно быть уникальным):')
    await state.set_state(TeamFSM.name)


@router.message(TeamFSM.name)
async def create_team_name(msg: Message, state: FSMContext):
    await msg.answer(f'Команда '{msg.text}' создана! Теперь пригласите участников.')
    await state.clear()


@router.message(commands=['join_team'])
async def join_team_start(msg: Message, state: FSMContext):
    await msg.answer('Введите код приглашения команды:')
    await state.set_state(TeamFSM.join_code)


@router.message(TeamFSM.join_code)
async def join_team_code(msg: Message, state: FSMContext):
    await msg.answer(f'Вы вступили в команду с кодом {msg.text}!')
    await state.clear()


@router.message(commands=['my_team'])
async def my_team(msg: Message):
    await msg.answer('Ваша команда: ... (участники)')


@router.message(commands=['leave_team'])
async def leave_team(msg: Message):
    await msg.answer('Вы покинули команду.')