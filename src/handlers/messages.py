from aiogram import F, Router
from aiogram.types import BufferedInputFile, Message
from aiogram.filters import Command, CommandObject
from database.actions import get_or_create_user
from database.models import User, Message as ModelMessage
from datetime import datetime
import keyboards
import settings
from random import choice, shuffle


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
            text=settings.TEXT_EVENT_STARTED.format(user=await User.get(id=user.secret_user_id)),
        )

    await message.answer(text=settings.TEXT_ADMIN_START_EVENT_USERS_NOTIFIED)


@router.message(Command(commands=['stop_event']))
async def stop_event(message: Message, command: CommandObject) -> None:
    if message.chat.id != settings.ADMIN_GROUP_ID:
        return

    users = User.filter(confirmed=True)

    async for user in users:
        try:
            await message.bot.send_message(
                chat_id=user.tg_id,
                text=settings.TEXT_EVENT_STOPPED.format(user=await User.get(secret_user_id=user.id)),
            )
        except:
            await message.answer(text=f'Заблокировал бота {user.tg_id} {user}')
    
    await message.answer(text=settings.TEXT_ADMIN_STOP_EVENT_USERS_NOTIFIED)
    
    await User.all().delete()


@router.message(Command(commands=['get_db']))
async def get_db(message: Message, command: CommandObject) -> None:
    if message.chat.id != settings.ADMIN_GROUP_ID:
        return

    users = await User.all().order_by('created_at')

    fields = (
        'id', 'tg_id', 'tg_username', 'tg_first_name', 'tg_last_name', 'created_at', 'name',
        'surname', 'additional_info', 'confirmed', 'secret_user_id', 'status',
    )

    html_table = (
        f'<thead><tr>{''.join(f'<td><b>{col}</b></td>' for col in fields)}</tr></thead>'
        f'<tbody>{''.join(f'<tr>{''.join(f'<td>{getattr(user, field)}</td>' for field in fields)}</tr>' for user in users)}</tbody>'
    )
    
    html_document = (
        '<!doctype html><html lang="ru">'
        '<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Users</title><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" '
        'rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">'
        f'</head><body><div class="p-4"><table class="table table-striped table-hover table-bordered">{html_table}</table></div>'
        '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" '
        'integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script></body></html>'
    )
    
    await message.bot.send_document(
        chat_id=message.chat.id,
        document=BufferedInputFile(html_document.encode('utf-8'), 'users.html'),
        caption='users',
    )
    

@router.message(Command(commands=['del_user']))
async def del_user(message: Message, command: CommandObject) -> None:
    if message.chat.id != settings.ADMIN_GROUP_ID:
        return
    
    user_id = command.args
    
    if user_id is None or not user_id.isdigit():
        await message.answer('<code>/del_user [tg_id]</code>')
        return
    
    user = await User.get_or_none(tg_id=user_id)

    if user is None:
        await message.answer('Пользователь не найден')
        return
    
    await user.delete()
    await message.answer('Пользователь удален')


@router.message(Command(commands=['send_santa']))
async def send_santa(message: Message, command: CommandObject) -> None:
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
async def send_recipient(message: Message, command: CommandObject) -> None:
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
async def cancel_command(message: Message, command: CommandObject) -> None:
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
    if message.chat.id == settings.ADMIN_GROUP_ID:
        return

    user = await get_or_create_user(message.from_user)

    if user.status == 'send-santa':
        santa = await User.get(secret_user_id=user.id)
        try:
            await message.bot.send_message(
                chat_id=santa.tg_id,
                text=settings.TEXT_MESSAGE_FROM_RECIPIENT.format(message=message.text),
            )
        except:
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
            )
        except:
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
