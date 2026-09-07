import asyncio
from aiogram import Bot, Dispatcher
import config
from plugins import greetings


async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Plagginlarni (Router) ulash
    dp.include_router(greetings.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())