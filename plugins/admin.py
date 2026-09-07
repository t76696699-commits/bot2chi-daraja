from pyrogram import Client, filters
from pyrogram.types import Message
import config

# Admin ekanligini tekshirish uchun custom filter
async def is_admin_filter(_, __, message: Message):
    return message.from_user and message.from_user.id in config.ADMIN_IDS

admin_only = filters.create(is_admin_filter)

@Client.on_message(filters.command("ban") & admin_only)
async def ban_handler(client: Client, message: Message):
    await message.reply_text("Foydalanuvchi muvaffaqiyatli ban qilindi (simulyatsiya)!")