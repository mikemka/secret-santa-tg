from aiogram import F, Router
from aiogram.types import CallbackQuery
from database.models import User
import settings


router = Router(name=__name__)


@router.callback_query()
async def not_handled(callback_query: CallbackQuery) -> None:
    print(f'WARN: not handled {callback_query.data=}')
    await callback_query.answer()
    await callback_query.bot.send_message(
        chat_id=settings.ADMIN_GROUP_ID,
        text=f'⚠️ WARN: callback not handled {callback_query.data=} {callback_query.from_user.id=}',
    )
