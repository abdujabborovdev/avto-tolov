from aiogram import Bot
from aiogram.types import BotCommand


async def set_default_commands(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Botni ishga tushirish"),
            BotCommand(command="help", description="Yordam"),
            BotCommand(command="balance",description='Kabinetim'),
            BotCommand(command="buy_number",description='Hisob olish'),
            BotCommand(command="deposit", description='Pul kiritish'),
            BotCommand(command="my_numbers", description='Nomerlarim royhati'),
            BotCommand(command="support", description='Qolab quvatlash'),
            BotCommand(command="faq", description='Qolanma')
        ]
    )
