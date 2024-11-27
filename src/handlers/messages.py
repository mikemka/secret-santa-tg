from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from database.actions import get_or_create_user
from database.models import User
from datetime import datetime
import keyboards
import settings
from random import shuffle


router = Router(name=__name__)


@router.message(Command(commands=['start', 'help']))
async def start(message: Message, command: CommandObject) -> None:
    if message.chat.id == settings.ADMIN_GROUP_ID:
        await message.answer(text=settings.TEXT_ADMIN_START)
        return

    user = await get_or_create_user(message.from_user)

    if not settings.REGISTRATION_START_DATE <= datetime.now() <= settings.REGISTRATION_END_DATE:
        await message.answer(text=settings.TEXT_REGISTRATION_CLOSED)
        return

    if not user.name:
        await message.answer(
            text=settings.TEXT_START.format(user=user),
            reply_markup=keyboards.start_registration,
        )


@router.message(Command(commands=['start_event']))
async def start_event(message: Message, command: CommandObject) -> None:
    if message.chat.id != settings.ADMIN_GROUP_ID:
        return

    users = User.filter(confirmed=True)

    n = 0

    async for user in users:
        try:
            await message.bot.send_message(
                chat_id=user.tg_id,
                text=settings.TEXT_USER_TESTING_MESSAGE,
            )
        except:
            await message.answer(text=f'Заблокировал бота {user.tg_id} {user}')
            await user.delete()
            n += 1

    await message.answer(text=settings.TEXT_ADMIN_START_EVENT_USERS_DELETED.format(n=n))

    users = User.filter(confirmed=True)

    users = [user async for user in users]
    shuffle(users)

    await message.answer(text=settings.TEXT_ADMIN_START_EVENT_USERS_SHUFFLED)

    for idx in range(1, len(users) + 1):
        users[idx % len(users)].secret_user_id = users[idx - 1].id
        await users[idx % len(users)].save()

    await message.answer(text=settings.TEXT_ADMIN_START_EVENT_USERS_SET)

    async for user in User.filter(confirmed=True):
        await message.bot.send_message(
            chat_id=user.tg_id,
            text=settings.TEXT_EVENT_STARTED,
        )

    await message.answer(text=settings.TEXT_ADMIN_START_EVENT_USERS_NOTIFIED)


@router.message(Command(commands=['stop_event']))
async def stop_event(message: Message, command: CommandObject) -> None:
    if message.chat.id != settings.ADMIN_GROUP_ID:
        return

    users = User.filter(confirmed=True)

    async for user in users:
        try:
            secret_santa = await User.get(id=user.secret_user_id)
            await message.bot.send_message(
                chat_id=user.tg_id,
                text=settings.TEXT_USER_TESTING_MESSAGE,
            )
        except:
            await message.answer(text=f'Заблокировал бота {user.tg_id} {user}')
            await user.delete()
            n += 1


@router.message(Command(commands=['id']))
async def chat_id(message: Message, command: CommandObject) -> None:
    await message.answer(text=str(message.chat.id))


@router.message(F.text == settings.TEXT_START_REGISTRATION)
async def start_registration(message: Message) -> None:
    user = await get_or_create_user(message.from_user)
    
    if not settings.REGISTRATION_START_DATE <= datetime.now() <= settings.REGISTRATION_END_DATE:
        await message.answer(text=settings.TEXT_REGISTRATION_CLOSED)
        return
    
    if not user.name:
        user.status = 'registration-enter-name'
        await user.save()
        await message.answer(text=settings.TEXT_ENTER_NAME)


@router.message(F.text == settings.TEXT_CANCEL_REGISTRATION)
async def cancel_registration(message: Message) -> None:
    user = await get_or_create_user(message.from_user)
    
    if not settings.REGISTRATION_START_DATE <= datetime.now() <= settings.REGISTRATION_END_DATE:
        await message.answer(text=settings.TEXT_REGISTRATION_CLOSED)
        return
    
    if user.name and user.surname and user.additional_info and user.status == 'registration-send_data' and not user.confirmed:
        await user.delete()
        await message.answer(text=settings.TEXT_REGISTRATION_CANCELLED)


@router.message(F.text == settings.TEXT_SEND_REGISTRATION_DATA)
async def process_registration(message: Message) -> None:
    user = await get_or_create_user(message.from_user)
    
    if not settings.REGISTRATION_START_DATE <= datetime.now() <= settings.REGISTRATION_END_DATE:
        await message.answer(text=settings.TEXT_REGISTRATION_CLOSED)
        return
    
    if user.name and user.surname and user.additional_info and user.status == 'registration-send_data' and not user.confirmed:
        await message.answer(text=settings.TEXT_PROCESSING_REGISTRATION)
        await message.bot.send_message(
            chat_id=settings.ADMIN_GROUP_ID,
            text=f'{settings.TEXT_MODERATION_NEW_USER}\n{settings.TEXT_MODERATION_USER_DATA}'.format(user=user),
            reply_markup=await keyboards.create_confirm_reject_registration(user_id=user.id),
        )
        user.status = 'registration-moderation'
        await user.save()


@router.message()
async def main_message(message: Message) -> None:
    user = await get_or_create_user(message.from_user)

    if not settings.REGISTRATION_START_DATE <= datetime.now() <= settings.REGISTRATION_END_DATE:
        await message.answer(text=settings.TEXT_REGISTRATION_CLOSED)
        return

    if not user.name and user.status == 'registration-enter-name':
        user.name = message.text.title()
        user.status = 'registration-enter-surname'
        await user.save()
        await message.answer(text=settings.TEXT_ENTER_SURNAME.format(user=user))
        return

    if user.name and not user.surname and user.status == 'registration-enter-surname':
        user.surname = message.text.title()
        user.status = 'registration-enter-additional-info'
        await user.save()
        await message.answer(text=settings.TEXT_ENTER_ADDITIONAL_INFO.format(user=user))
        return

    if user.name and user.surname and not user.additional_info and user.status == 'registration-enter-additional-info':
        user.additional_info = message.text.upper()
        user.status = 'registration-send_data'
        await user.save()
        await message.answer(
            text=settings.TEXT_REGISTRATION_END.format(user=user),
            reply_markup=keyboards.send_registration_data,
        )
        return