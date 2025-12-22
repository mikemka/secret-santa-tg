from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from database.actions import get_or_create_user
from database.models import User, Message as ModelMessage
from datetime import datetime
import keyboards
import settings


router = Router(name=__name__)


@router.message(Command(commands=['start', 'help']))
async def start(message: Message) -> None:
    user = await get_or_create_user(message.from_user)
    
    if user.confirmed and not settings.REGISTRATION_START_DATE <= datetime.now() <= settings.REGISTRATION_END_DATE:
        await message.answer(text=settings.TEXT_EVENT_STARTED.format(user=await User.get(id=user.secret_user_id)))
        return

    if not settings.REGISTRATION_START_DATE <= datetime.now() <= settings.REGISTRATION_END_DATE:
        await message.answer(text=settings.TEXT_REGISTRATION_CLOSED)
        return

    if not user.name and not user.status:
        await message.answer(
            text=settings.TEXT_START.format(user=user),
            reply_markup=keyboards.start_registration,
        )
    
    if user.status == 'registration-enter-name':
        await message.answer(text=settings.TEXT_ENTER_NAME.format(user=user))
    
    if user.status == 'registration-enter-surname':
        await message.answer(text=settings.TEXT_ENTER_SURNAME.format(user=user))

    if user.status == 'registration-enter-additional-info':
        await message.answer(text=settings.TEXT_ENTER_ADDITIONAL_INFO.format(user=user))

    if user.status == 'registration-send_data':
        await message.answer(
            text=settings.TEXT_REGISTRATION_END.format(user=user),
            reply_markup=keyboards.send_registration_data,
        )
    
    if user.status == 'registration-moderation':
        await message.answer(text=settings.TEXT_PROCESSING_REGISTRATION.format(user=user))
    
    if user.status == 'registration-moderation-confirmed':
        await message.answer(text=settings.TEXT_REGISTRATION_CONFIRMED)


@router.message(Command(commands=['send_santa']))
async def send_santa(message: Message) -> None:
    user = await get_or_create_user(message.from_user)
    if not user.confirmed or not user.secret_user_id:
        return

    user.status = 'send-santa'
    await user.save()

    await message.bot.send_message(
        chat_id=user.tg_id,
        text=settings.TEXT_MESSAGE_TO_SANTA,
    )


@router.message(Command(commands=['send_recipient']))
async def send_recipient(message: Message) -> None:
    user = await get_or_create_user(message.from_user)
    if not user.confirmed or not user.secret_user_id:
        return

    user.status = 'send-recipient'
    await user.save()

    await message.bot.send_message(
        chat_id=user.tg_id,
        text=settings.TEXT_MESSAGE_TO_RECIPIENT,
    )


@router.message(Command(commands=['cancel']))
async def cancel_command(message: Message) -> None:
    user = await get_or_create_user(message.from_user)
    if not user.confirmed or not user.secret_user_id:
        return

    user.status = ''
    await user.save()

    await message.bot.send_message(
        chat_id=user.tg_id,
        text=settings.TEXT_CANCEL,
    )


@router.message(Command(commands=['id']))
async def chat_id(message: Message) -> None:
    await message.answer(text=f'ID чата: <code>{message.chat.id}</code>\nID пользователя: <code>{message.from_user.id}</code>')


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
        admin_group_message = await message.bot.send_message(
            chat_id=settings.ADMIN_GROUP_ID,
            text=f'{settings.TEXT_MODERATION_NEW_USER}\n{settings.TEXT_MODERATION_USER_DATA}'.format(user=user),
            reply_markup=await keyboards.create_confirm_reject_registration(user_id=user.id),
        )
        user.status = 'registration-moderation'
        await user.save()

        await message.bot.pin_chat_message(
            chat_id=settings.ADMIN_GROUP_ID,
            message_id=admin_group_message.message_id,
            disable_notification=True,
        )


@router.message()
async def main_message(message: Message) -> None:
    user = await get_or_create_user(message.from_user)

    if user.status == 'send-santa':
        santa = await User.get(secret_user_id=user.id)
        try:
            await message.bot.send_message(
                chat_id=santa.tg_id,
                text=settings.TEXT_MESSAGE_FROM_RECIPIENT.format(message=message.text),
                parse_mode=None,
            )
        except Exception as e:
            print(e)
            await message.answer(text=settings.TEXT_SANTA_BITCH.format(user=santa))
            await santa.delete()
            await message.bot.send_message(
                chat_id=settings.ADMIN_GROUP_ID,
                text=f'Заблокировал бота\n{settings.TEXT_MODERATION_USER_DATA}'.format(user=santa),
            )
        await ModelMessage.create(from_user=user, to_user=santa, text=settings.TEXT_MESSAGE_FROM_RECIPIENT.format(message=message.text))
        user.status = ''
        await user.save()
        await message.answer(text=settings.TEXT_MESSAGE_SENT_SUCCESS)
        return

    if user.status == 'send-recipient':
        recipient = await User.get(id=user.secret_user_id)
        try:
            await message.bot.send_message(
                chat_id=recipient.tg_id,
                text=settings.TEXT_MESSAGE_FROM_SANTA.format(message=message.text),
                parse_mode=None,
            )
        except Exception as e:
            print(e)
            await message.answer(text=settings.TEXT_RECIPIENT_BITCH.format(user=recipient))
            await recipient.delete()
            await message.bot.send_message(
                chat_id=settings.ADMIN_GROUP_ID,
                text=f'Заблокировал бота\n{settings.TEXT_MODERATION_USER_DATA}'.format(user=recipient),
            )
        await ModelMessage.create(from_user=user, to_user=recipient, text=settings.TEXT_MESSAGE_FROM_SANTA.format(message=message.text))
        user.status = ''
        await user.save()
        await message.answer(text=settings.TEXT_MESSAGE_SENT_SUCCESS)
        return

    if user.secret_user_id:
        await message.answer(text=settings.TEXT_EVENT_STARTED)
        return

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
