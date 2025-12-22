from aiogram import F, Router
from aiogram.types import BufferedInputFile, Message
from aiogram.filters import Command, CommandObject
from database.actions import get_or_create_user
from database.models import User, Message as ModelMessage
from datetime import datetime
import keyboards
import settings
from random import shuffle
from tortoise.expressions import Q


router = Router(name=__name__)
router.message.filter(
    F.chat.id == settings.ADMIN_GROUP_ID,
)


@router.message(Command(commands=['start', 'help', 'admin']))
async def start(message: Message) -> None:
    await message.answer(text=settings.TEXT_ADMIN_START)


@router.message(Command(commands=['start_event']))
async def start_event(message: Message) -> None:
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
async def stop_event(message: Message) -> None:
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
async def get_db(message: Message) -> None:
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
        f'</head><body><div class="p-4"><table class="table table-hover table-bordered">{html_table}</table></div>'
        '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" '
        'integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script></body></html>'
    )
    
    await message.bot.send_document(
        chat_id=message.chat.id,
        document=BufferedInputFile(html_document.encode('utf-8'), 'users.html'),
        caption='users',
    )
    
    html_payload = ''

    for santa in users:
        # Загружаем получателя (секретного друга)
        try:
            recipient = await User.get(id=santa.secret_user_id)
        except:
            continue

        html_dialog = (
            f'<h2 class="pair-title">Santa: {santa}; Recipient: {recipient}</h2>'
            '<div class="dialog-box">'
        )

        # Загружаем все сообщения между парой
        messages = await ModelMessage.filter(
            Q(from_user=santa, to_user=recipient) |
            Q(from_user=recipient, to_user=santa)
        ).order_by('created_at')

        for msg in messages:
            sender_is_santa = (msg.from_user_id == santa.id)

            html_dialog += (
                '<div class="msg-container">'
                f'<div class="msg {"santa" if sender_is_santa else "recipient"}">'
                f'{msg.text}'
                f'<span class="msg-time">{msg.created_at.strftime("%Y-%m-%d %H:%M")}</span>'
                '</div></div>'
            )

        html_dialog += '</div>'
        html_payload += html_dialog


    html_document = (
        '<!doctype html><html lang="ru">'
        '<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Messages</title>'
        '<link href="https://mikemka.github.io/secret-santa-tg/assets/dbStyles.css" rel="stylesheet">'
        '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">'
        '</head>'
        f'<body><div class="p-4"><h1>Messages</h1>{html_payload}</div>'
        '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>'
        '</body></html>'
    )

    await message.bot.send_document(
        chat_id=message.chat.id,
        document=BufferedInputFile(html_document.encode('utf-8'), 'messages.html'),
        caption='messages',
    )


@router.message(Command(commands=['count_users']))
async def count_users(message: Message) -> None:
    await message.answer(
        f'Пользователей зарегистрировано: {await User.all().count()}\n'
        f'Пользователей подтвердилось: {await User.filter(confirmed=True).count()}',
    )


@router.message(Command(commands=['del_user']))
async def del_user(message: Message, command: CommandObject) -> None:
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


@router.message(Command(commands=['add_user']))
async def add_user(message: Message, command: CommandObject) -> None:
    async def send_help() -> None:
        await message.answer(
            '<code>'
            '/add_user\n'
            '[tg_id: int]\n'
            '[tg_username: str | None]\n'
            '[tg_first_name: str]\n'
            '[tg_last_name: str | None]\n'
            '[name: str]\n'
            '[surname: str]\n'
            '[additional_info: str]\n'
            '</code>',
        )

    data = command.args

    if data is None:
        await send_help()
        return

    data = data.strip().split('\n')

    if len(data) != 7:
        await send_help()
        return

    user, _ = await User.update_or_create(
        defaults={
            'tg_username': data[1] if data[1] != 'None' else None,
            'tg_first_name': data[2],
            'tg_last_name': data[3] if data[3] != 'None' else None,
            'name': data[4],
            'surname': data[5],
            'additional_info': data[6],
            'confirmed': True,
            'status': 'registration-moderation-confirmed',
        },
        tg_id=int(data[0]),
    )

    await message.answer(
        f'Пользователь добавлен:\n'
        f'{user.tg_id=}\n'
        f'{user.tg_username=}\n'
        f'{user.tg_first_name=}\n'
        f'{user.tg_last_name=}\n'
        f'{user.name=}\n'
        f'{user.surname=}\n'
        f'{user.additional_info=}\n'
        f'{user.confirmed=}\n'
        f'{user.status=}\n'
    )


@router.message(Command(commands=['mail']))
async def mail(message: Message, command: CommandObject) -> None:
    args = command.args
    if not args:
        await message.answer('<code>/mail [текст рассылки (html разметка)]</code>')
        return
    try:
        await message.bot.send_message(
            chat_id=settings.ADMIN_GROUP_ID,
            text=args.strip(),
            reply_markup=await keyboards.create_mailing_keyboard(),
        )
    except Exception as e:
        await message.answer(f'Ошибка: {e}')


@router.message()
async def main_message(message: Message) -> None:
    pass
