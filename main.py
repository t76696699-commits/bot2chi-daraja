import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.account import GetAuthorizationsRequest

load_dotenv()
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["TELETHON_SESSION_STRING"]


async def audit() -> None:
    async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
        result = await client(GetAuthorizationsRequest())
        print(f"Jami faol seanslar: {len(result.authorizations)}\n")
        for auth in result.authorizations:
            marker = "JORIY" if auth.current else "boshqa qurilma"
            print(f"[{marker}] {auth.device_model} ({auth.platform}) -- {auth.country}")
            print(f"        so'nggi faollik: {auth.date_active}, hash={auth.hash}")


if __name__ == "__main__":
    asyncio.run(audit())