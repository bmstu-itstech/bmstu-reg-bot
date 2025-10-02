import asyncio
from handlers.team import router as team_router
from handlers.profile import router as profile_router
from handlers.registration import router as registration_router

import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from dotenv import load_dotenv


async def main():
    load_dotenv("./.env")
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN not found")

    bot = Bot(token=token)

    dp = Dispatcher()

    dp.include_router(team_router)
    dp.include_router(profile_router)
    dp.include_router(registration_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())