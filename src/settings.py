from ast import literal_eval
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from os import getenv


# * .env File

BASE_DIR = Path(__file__).resolve().parent.parent

DOTENV_PATH = BASE_DIR / '.env'

if DOTENV_PATH.exists():
    load_dotenv(DOTENV_PATH)

# * Loading Environment

DEBUG = literal_eval(getenv('DEBUG').title())
USE_WEBHOOK = literal_eval(getenv('USE_WEBHOOK').title())

# * Telegram

TOKEN = getenv('TOKEN')
ADMIN_GROUP_ID = int(getenv('ADMIN_GROUP_ID'))

# * Telegram Webhook

WEB_SERVER_HOST = WEB_SERVER_PORT = WEBHOOK_PATH = WEBHOOK_SECRET = BASE_WEBHOOK_URL = 0

if USE_WEBHOOK:
    WEB_SERVER_HOST = getenv('WEB_SERVER_HOST')
    WEB_SERVER_PORT = int(getenv('WEB_SERVER_PORT'))
    WEBHOOK_PATH = getenv('WEBHOOK_PATH').strip('/')
    WEBHOOK_SECRET = getenv('WEBHOOK_SECRET')
    BASE_WEBHOOK_URL = getenv('BASE_WEBHOOK_URL').rstrip('/')

    assert BASE_WEBHOOK_URL.startswith('https://')

# * Database

DB_URL = getenv('DB_URL')

REGISTRATION_START_DATE = datetime.fromisoformat(getenv('REGISTRATION_START_DATE'))
REGISTRATION_END_DATE = datetime.fromisoformat(getenv('REGISTRATION_END_DATE'))

# * Texts

TEXT_START = getenv('TEXT_START').replace('\\n', '\n')
TEXT_REGISTRATION_CLOSED = getenv('TEXT_REGISTRATION_CLOSED').replace('\\n', '\n')
TEXT_START_REGISTRATION = getenv('TEXT_START_REGISTRATION').replace('\\n', '\n')
TEXT_ENTER_NAME = getenv('TEXT_ENTER_NAME').replace('\\n', '\n')
TEXT_ENTER_SURNAME = getenv('TEXT_ENTER_SURNAME').replace('\\n', '\n')
TEXT_ENTER_ADDITIONAL_INFO = getenv('TEXT_ENTER_ADDITIONAL_INFO').replace('\\n', '\n')
TEXT_REGISTRATION_END = getenv('TEXT_REGISTRATION_END').replace('\\n', '\n')
TEXT_SEND_REGISTRATION_DATA = getenv('TEXT_SEND_REGISTRATION_DATA').replace('\\n', '\n')
TEXT_CANCEL_REGISTRATION = getenv('TEXT_CANCEL_REGISTRATION').replace('\\n', '\n')
TEXT_REGISTRATION_CANCELLED = getenv('TEXT_REGISTRATION_CANCELLED').replace('\\n', '\n')
TEXT_PROCESSING_REGISTRATION = getenv('TEXT_PROCESSING_REGISTRATION').replace('\\n', '\n')
TEXT_REGISTRATION_CONFIRMED = getenv('TEXT_REGISTRATION_CONFIRMED').replace('\\n', '\n')
TEXT_REGISTRATION_REJECTED = getenv('TEXT_REGISTRATION_REJECTED').replace('\\n', '\n')

TEXT_MODERATION_NEW_USER = getenv('TEXT_MODERATION_NEW_USER').replace('\\n', '\n')
TEXT_MODERATION_USER_DATA = getenv('TEXT_MODERATION_USER_DATA').replace('\\n', '\n')
TEXT_MODERATION_CONFIRM = getenv('TEXT_MODERATION_CONFIRM').replace('\\n', '\n')
TEXT_MODERATION_REJECT = getenv('TEXT_MODERATION_REJECT').replace('\\n', '\n')
TEXT_MODERATION_CONFIRMED = getenv('TEXT_MODERATION_CONFIRMED').replace('\\n', '\n')
TEXT_MODERATION_REJECTED = getenv('TEXT_MODERATION_REJECTED').replace('\\n', '\n')

TEXT_ADMIN_START = getenv('TEXT_ADMIN_START').replace('\\n', '\n')

TEXT_USER_TESTING_MESSAGE = getenv('TEXT_USER_TESTING_MESSAGE').replace('\\n', '\n')

TEXT_ADMIN_START_EVENT_USERS_DELETED = getenv('TEXT_ADMIN_START_EVENT_USERS_DELETED').replace('\\n', '\n')
TEXT_ADMIN_START_EVENT_USERS_SHUFFLED = getenv('TEXT_ADMIN_START_EVENT_USERS_SHUFFLED').replace('\\n', '\n')
TEXT_ADMIN_START_EVENT_USERS_SET = getenv('TEXT_ADMIN_START_EVENT_USERS_SET').replace('\\n', '\n')
TEXT_ADMIN_START_EVENT_USERS_NOTIFIED = getenv('TEXT_ADMIN_START_EVENT_USERS_NOTIFIED').replace('\\n', '\n')

TEXT_ADMIN_STOP_EVENT_USERS_NOTIFIED = getenv('TEXT_ADMIN_STOP_EVENT_USERS_NOTIFIED').replace('\\n', '\n')

TEXT_EVENT_STARTED = getenv('TEXT_EVENT_STARTED').replace('\\n', '\n')
TEXT_EVENT_STOPPED = getenv('TEXT_EVENT_STOPPED').replace('\\n', '\n')

TEXT_SANTA_BITCH = getenv('TEXT_SANTA_BITCH').replace('\\n', '\n')
TEXT_RECIPIENT_BITCH = getenv('TEXT_RECIPIENT_BITCH').replace('\\n', '\n')

TEXT_MESSAGE_TO_SANTA = getenv('TEXT_MESSAGE_TO_SANTA').replace('\\n', '\n')
TEXT_MESSAGE_TO_RECIPIENT = getenv('TEXT_MESSAGE_TO_RECIPIENT').replace('\\n', '\n')
TEXT_MESSAGE_FROM_SANTA = getenv('TEXT_MESSAGE_FROM_SANTA').replace('\\n', '\n')
TEXT_MESSAGE_FROM_RECIPIENT = getenv('TEXT_MESSAGE_FROM_RECIPIENT').replace('\\n', '\n')

TEXT_CANCEL = getenv('TEXT_CANCEL').replace('\\n', '\n')

TEXT_MESSAGE_SENT_SUCCESS = getenv('TEXT_MESSAGE_SENT_SUCCESS').replace('\\n', '\n')
