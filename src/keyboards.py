from aiogram.types import (
    KeyboardButton as RButton,
    ReplyKeyboardMarkup as RMarkup,
    InlineKeyboardMarkup as IMarkup,
    InlineKeyboardButton as IButton
)
import settings
from random import shuffle


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


MAILING_CANCELLED = IMarkup(
    inline_keyboard=[
        [
            IButton(text='❌ Рассылка отменена', callback_data='mailing_pass'),
        ]
    ]
)


async def mailing_sent_info_keyboard(
    ok: int | None = None,
    fail: int | None = None,
) -> IMarkup:
    if ok is None or fail is None:
        return IMarkup(
            inline_keyboard=[
                [
                    IButton(text='✈️ Идет рассылка', callback_data='mailing_pass'),
                ]
            ]
        )
    return IMarkup(
        inline_keyboard=[
            [
                IButton(text=f'✅ Отправлено: {ok}', callback_data='mailing_pass'),
                IButton(text=f'❌ Ошибка: {fail}', callback_data='mailing_pass'),
            ]
        ]
    )


async def create_mailing_keyboard() -> IMarkup:
    buttons = [
        *(
            IButton(text=f'{'🙅🚫🙊❌😶'[i]} Отменить', callback_data='cancel_mailing')
            for i in range(5)
        ),
        IButton(text='📤 Отправить', callback_data='send_mailing'),
    ]
    shuffle(buttons)
    
    return IMarkup(
        inline_keyboard=[
            buttons[:3],
            buttons[3:],
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
