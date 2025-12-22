from handlers.admin_messages import router as admin_messages_router
from handlers.admin_callback import router as admin_callback_router
from handlers.callback import router as callback_router
from handlers.messages import router as messages_router


routers = [
    admin_callback_router,
    admin_messages_router,
    callback_router,
    messages_router,
]
