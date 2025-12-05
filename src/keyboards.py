from aiogram.types import (
    KeyboardButton as RButton,
    ReplyKeyboardMarkup as RMarkup,
    InlineKeyboardMarkup as IMarkup,
    InlineKeyboardButton as IButton
)
import settings


start_registration = RMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
    keyboard=[
        [
            RButton(text=settings.TEXT_START_REGISTRATION),
        ],
    ],
)

send_registration_data = RMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
    keyboard=[
        [
            RButton(text=settings.TEXT_SEND_REGISTRATION_DATA),
        ],
        [
            RButton(text=settings.TEXT_CANCEL_REGISTRATION),
        ],
    ],
)

async def create_confirm_reject_registration(user_id: int) -> IMarkup:
    return IMarkup(
        inline_keyboard=[
            [
                IButton(text=settings.TEXT_MODERATION_CONFIRM, callback_data=f'confirm-registration-{user_id}'),
                IButton(text=settings.TEXT_MODERATION_REJECT, callback_data=f'reject-registration-{user_id}'),
            ],
        ],
    )
