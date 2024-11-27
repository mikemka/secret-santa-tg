from aiogram.types import User as TgUser
from database.models import User


async def get_or_create_user(from_user: TgUser) -> User:
    return (await User.get_or_create(
        defaults={
            'tg_username': from_user.username,
            'tg_first_name': from_user.first_name,
            'tg_last_name': from_user.last_name,
            'tg_id': from_user.id,
        },
        tg_id=from_user.id,
    ))
