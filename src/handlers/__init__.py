from handlers.callback import router as callback_router
from handlers.messages import router as messages_router


routers = [
    callback_router,
    messages_router,
]
