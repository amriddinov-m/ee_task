import asyncio
import logging
import os
import sys

import django
from aiogram import Bot
from bot.utils.set_bot_commands import set_default_commands


def setup_django():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "ee_task.settings"
    )
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    django.setup()


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    from bot.handlers import dp
    bot = Bot(token='7073719708:AAGdPGW9_DvZRG-zeuWpTE4iiGHpmZkbbZU')
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == '__main__':
    setup_django()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
