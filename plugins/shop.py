from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("shop"))
async def shop_handler(client: Client, message: Message):
    products = (
        "🛒 **Bizning do'konimizdagi mahsulotlar:**\n\n"
        "1. Python kursi — 100$\n"
        "2. Pyrogram bot yaratish — 50$\n"
        "3. Django backend — 120$"
    )
    await message.reply_text(products)