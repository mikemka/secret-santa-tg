from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from database.actions import init_db, shutdown_db
from asyncio import run
from handlers import routers
import logging
import settings
import sys


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(
        f"{settings.BASE_WEBHOOK_URL}/{settings.WEBHOOK_PATH}",
        secret_token=settings.WEBHOOK_SECRET,
    )


async def ping(request):
    return web.Response(text='OK')


def run_with_webhooks() -> None:
    dp = Dispatcher()
    
    dp.startup.register(on_startup)
    
    dp.include_routers(*routers)
    bot = Bot(
        settings.TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    app = web.Application()
    
    app.router.add_get('/ping', ping)
    app.router.add_get('/ping/', ping)
    
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=f'/{settings.WEBHOOK_PATH}')
    
    setup_application(app, dp, bot=bot)
    web.run_app(
        app,
        host=settings.WEB_SERVER_HOST,
        port=settings.WEB_SERVER_PORT,
    )


async def run_with_polling() -> None:
    bot = Bot(
        settings.TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    dp.include_routers(*routers)
    
    await init_db()
    
    try:
        await dp.start_polling(bot)
    finally:
        await shutdown_db()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO if settings.DEBUG else logging.WARNING,
        stream=sys.stdout,
    )
    if settings.USE_WEBHOOK:
        run(init_db())
        run_with_webhooks()
    else:
        run(run_with_polling())
