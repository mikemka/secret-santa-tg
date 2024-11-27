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

# weather_keyboard = InMarkup(inline_keyboard=[
#     [
#         InButton(text='📆 Прогноз на сегодня', callback_data='weather-days-1'),
#     ],
#     [
#         InButton(text='🗓 Прогноз на 3 дня', callback_data='weather-days-3'),
#     ],
# ])


# select_country_keyboard = InMarkup(inline_keyboard=[
#     *([[
#         InButton(text=COUNTRIES[0].title, callback_data=f'select-country-{COUNTRIES[0].data}'),
#     ]] if len(COUNTRIES) % 2 else [[]]),
#     *([
#         InButton(text=COUNTRIES[idx].title, callback_data=f'select-country-{COUNTRIES[idx].data}'),
#         InButton(text=COUNTRIES[idx + 1].title, callback_data=f'select-country-{COUNTRIES[idx + 1].data}'),
#     ] for idx in range(len(COUNTRIES) % 2, len(COUNTRIES), 2)),
# ])


# async def create_select_city_keyboard(country: str) -> InMarkup:
#     cities = [_country.cities for _country in COUNTRIES if _country.data == country][0]
    
#     return InMarkup(inline_keyboard=[
#         *([[
#             InButton(text=cities[0].title, callback_data=f'select-city-{country}-{cities[0].title}'),
#         ]] if len(cities) % 2 else [[]]),
#         *([
#             InButton(text=cities[idx].title, callback_data=f'select-city-{country}-{cities[idx].title}'),
#             InButton(text=cities[idx + 1].title, callback_data=f'select-city-{country}-{cities[idx + 1].title}'),
#         ] for idx in range(len(cities) % 2, len(cities), 2)),
#     ])


# async def create_settings_keyboard(user: User) -> InMarkup:
#     avaliable_cities = [_country.cities for _country in COUNTRIES if _country.data == user.country][0]

#     print(avaliable_cities)
    
#     return InMarkup(inline_keyboard=[
#         [
#             InButton(
#                 text=[_country.title for _country in COUNTRIES if _country.data == user.country][0],
#                 callback_data='to-select-country',
#             ),
#             InButton(text=f'📍 г. {user.city}', callback_data=f'to-select-city-{user.country}'),
#         ],
#     ])
