from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Assalomu alaykum! Botga xush kelibsiz.")

@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer("Mavjud buyruqlar: /start, /help, /shop, /ban")