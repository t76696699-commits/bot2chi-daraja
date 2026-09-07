import time
import asyncio
from pyrogram import Client
import config


def is_tgcrypto_active() -> bool:
    """TgCrypto kutubxonasi o'rnatilganligini va faolligini tekshiradi."""
    try:
        import tgcrypto
        return True
    except ImportError:
        return False


async def benchmark_history_read(app: Client, chat_id: str | int, limit: int = 300):
    """Chatdagi xabarlarni o'qish vaqtini o'lchaydi."""
    start_time = time.perf_counter()

    count = 0
    async for message in app.get_chat_history(chat_id, limit=limit):
        count += 1

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    tgcrypto_status = "O'rnatilgan (Aktiv)" if is_tgcrypto_active() else "O'rnatilmagan (Aktiv emas)"

    print(f"\n--- BENCHMARK NATIJASI ---")
    print(f"TgCrypto holati: {tgcrypto_status}")
    print(f"O'qilgan xabarlar soni: {count}")
    print(f"Ketgan vaqt: {execution_time:.4f} soniya\n")
    return execution_time


async def main():
    app = Client(
        "benchmark_session",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN
    )

    async with app:
        # 'me' o'rniga istalgan kanal/chat username yoki ID-sini berishingiz mumkin
        await benchmark_history_read(app, chat_id="me", limit=300)


if __name__ == "__main__":
    asyncio.run(main())