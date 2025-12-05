from aiogram import F, Router
from aiogram.types import CallbackQuery
from database.models import User
import settings


router = Router(name=__name__)


@router.callback_query(F.data.startswith('confirm-registration-'))
async def confirm_registration_callback_handler(callback_query: CallbackQuery) -> None:
    if callback_query.message.chat.id != settings.ADMIN_GROUP_ID:
        return
    
    user_id = int(callback_query.data.split('-')[-1])
    user = await User.get(id=user_id)
    user.confirmed = True
    user.status = 'registration-moderation-confirmed'
    await user.save()
    await callback_query.bot.send_message(
        chat_id=user.tg_id,
        text=settings.TEXT_REGISTRATION_CONFIRMED,
    )
    await callback_query.message.edit_text(
        text=f'{settings.TEXT_MODERATION_CONFIRMED}\n\n{settings.TEXT_MODERATION_USER_DATA}'.format(user=user),
        reply_markup=None,
    )
    
    await callback_query.bot.unpin_chat_message(
        chat_id=settings.ADMIN_GROUP_ID,
        message_id=callback_query.message.message_id,
    )
    
    await callback_query.answer()


@router.callback_query(F.data.startswith('reject-registration-'))
async def reject_registration_callback_handler(callback_query: CallbackQuery) -> None:
    if callback_query.message.chat.id != settings.ADMIN_GROUP_ID:
        return
    
    user_id = int(callback_query.data.split('-')[-1])
    user = await User.get(id=user_id)
    user_tg_id = user.tg_id
    await user.delete()
    await callback_query.bot.send_message(
        chat_id=user_tg_id,
        text=settings.TEXT_REGISTRATION_REJECTED,
    )
    await callback_query.message.edit_text(
        text=f'{settings.TEXT_MODERATION_REJECTED}\n\n{settings.TEXT_MODERATION_USER_DATA}'.format(user=user),
        reply_markup=None,
    )
    
    await callback_query.bot.unpin_chat_message(
        chat_id=settings.ADMIN_GROUP_ID,
        message_id=callback_query.message.message_id,
    )
    
    await callback_query.answer()


@router.callback_query()
async def not_handled(callback_query: CallbackQuery) -> None:
    print(f'WARN: not handled {callback_query.data=}')
    await callback_query.answer()
    await callback_query.bot.send_message(
        chat_id=settings.ADMIN_GROUP_ID,
        text=f'⚠️ WARN: callback not handled {callback_query.data=} {callback_query.from_user.id=}',
    )
