import os

from dotenv import load_dotenv


load_dotenv()


def env_required(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"{key} is not set")
    return value


BOT_TOKEN = env_required("BOT_TOKEN")
BOT_TELEGRAM_NAME = env_required("BOT_TELEGRAM_NAME")
DATABASE_URI = env_required("DATABASE_URI")

MAX_TEAMMATES = 3
