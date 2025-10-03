import asyncio
from aiogram import Bot, Dispatcher

from bot.handlers.team import router as team_router
from bot.handlers.profile import router as profile_router
from bot.handlers.registration import router as registration_router

import config


async def main():
    bot = Bot(token=config.BOT_TOKEN)

    dp = Dispatcher()

    dp.include_router(team_router)
    dp.include_router(profile_router)
    dp.include_router(registration_router)

    print("Bot started")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())