from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description="Botni ishga tushirish 🚀"
        ),
        BotCommand(
            command='help',
            description="Yordam va qo'llanma ❓"
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
