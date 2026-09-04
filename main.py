import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import (
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
    FloodWaitError,
)

load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

client = TelegramClient("namuna_session", API_ID, API_HASH)


async def main() -> None:
    await client.connect()
    if not await client.is_user_authorized():
        phone = os.environ.get("PHONE") or input("Telefon: ")
        try:
            sent = await client.send_code_request(phone)
            code = input("Kod: ")
            await client.sign_in(phone, code, phone_code_hash=sent.phone_code_hash)
        except SessionPasswordNeededError:
            await client.sign_in(password=input("2FA parol: "))
        except (PhoneNumberInvalidError, PhoneCodeInvalidError) as e:
            print(f"Login xatosi: {e}")
            return
        except FloodWaitError as e:
            print(f"{e.seconds} soniya kutish kerak.")
            return

    me = await client.get_me()
    print(f"Salom, {me.first_name}! (id={me.id})")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
