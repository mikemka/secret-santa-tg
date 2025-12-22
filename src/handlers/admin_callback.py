from aiogram import F, Router
from aiogram.types import CallbackQuery
from database.models import User
import settings
import keyboards


router = Router(name=__name__)
router.callback_query.filter(
    F.message.chat.id == settings.ADMIN_GROUP_ID,
)


@router.callback_query(F.data.startswith('confirm-registration-'))
async def confirm_registration_callback_handler(callback_query: CallbackQuery) -> None:
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


@router.callback_query(F.data == 'cancel_mailing')
async def cancel_mailing_callback_handler(callback_query: CallbackQuery) -> None:
    await callback_query.message.edit_reply_markup(
        reply_markup=keyboards.MAILING_CANCELLED,
    )
    await callback_query.answer()


@router.callback_query(F.data == 'mailing_pass')
async def mailing_pass_callback_handler(callback_query: CallbackQuery) -> None:
    await callback_query.answer()


@router.callback_query(F.data == 'send_mailing')
async def send_mailing_callback_handler(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
    await callback_query.message.edit_reply_markup(
        reply_markup=await keyboards.mailing_sent_info_keyboard(),
    )
    
    ok = 0
    errors = 0
    
    users = await User.all()
    for user in users:
        try:
            await callback_query.bot.send_message(
                chat_id=user.tg_id,
                text=callback_query.message.html_text,
            )
            ok += 1
        except:
            errors += 1

    await callback_query.message.edit_reply_markup(
        reply_markup=await keyboards.mailing_sent_info_keyboard(
            ok=ok,
            fail=errors,
        ),
    )
