# ═══════════════════════════════════════════════════════════════════════
# Outer va Inner middleware zanjiri: ishga tushirish tartibini isbotlash
# ═══════════════════════════════════════════════════════════════════════
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Router
from aiogram.types import Message, TelegramObject


class OuterLoggingMiddleware(BaseMiddleware):
    # Outer #1 — HAR bir update uchun ishlaydi.

    async def __call__(self, handler, event: TelegramObject, data: Dict[str, Any]) -> Any:
        print("-> OUTER logging: kirish")
        result = await handler(event, data)
        print("<- OUTER logging: chiqish")
        return result


class OuterAuthMiddleware(BaseMiddleware):
    # Outer #2 — HAR bir update uchun ishlaydi, logging ICHIDA.

    async def __call__(self, handler, event: TelegramObject, data: Dict[str, Any]) -> Any:
        print("-> OUTER auth: tekshirilmoqda")
        result = await handler(event, data)
        print("<- OUTER auth: tugadi")
        return result


class InnerLoadCartMiddleware(BaseMiddleware):
    # Inner #1 — FAQAT filtr mos kelgan handler uchun ishlaydi.

    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> Any:
        print("-> INNER savat yuklash")
        data["cart"] = {"items": []}  # odatda bazadan yuklanadi
        result = await handler(event, data)
        print("<- INNER savat: tozalash")
        return result


class InnerTimingMiddleware(BaseMiddleware):
    # Inner #2 — handlerga eng yaqin qatlam.

    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> Any:
        print("-> INNER timing: boshlandi")
        result = await handler(event, data)
        print("<- INNER timing: tugadi")
        return result


def register_middlewares(router: Router) -> None:
    # Ro'yxatdan o'tkazish tartibi = ichma-ich joylashish tartibi
    router.update.outer_middleware(OuterLoggingMiddleware())   # eng tashqi
    router.update.outer_middleware(OuterAuthMiddleware())
    router.message.middleware(InnerLoadCartMiddleware())
    router.message.middleware(InnerTimingMiddleware())          # handlerga eng yaqin


# Kutilgan konsol chiqishi mos handler topilganda:
# -> OUTER logging: kirish
# -> OUTER auth: tekshirilmoqda
# -> INNER savat yuklash
# -> INNER timing: boshlandi
#   (handler ishlaydi)
# <- INNER timing: tugadi
# <- INNER savat: tozalash
# <- OUTER auth: tugadi
# <- OUTER logging: chiqish


# ═══════════════════════════════════════════════════════════════════════
# Nested router'lar: admin_router va user_router asosiy dispetcherga ulanadi
# ═══════════════════════════════════════════════════════════════════════
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

admin_router = Router(name="admin")
user_router = Router(name="user")


@admin_router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    await message.answer("Statistika: faol foydalanuvchilar soni ...")


@user_router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer("Yordam: /start, /help buyruqlari mavjud.")


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    # Outer middleware'lar ASOSIY dispetcherga qo'yiladi — shu tufayli
    # admin_router HAM, user_router HAM ular orqali o'tadi, chunki
    # include_router qilingan router'lar ota dispetcherning outer
    # middleware'laridan chetlanib qololmaydi.
    dp.update.outer_middleware(OuterLoggingMiddleware())
    dp.update.outer_middleware(OuterAuthMiddleware())

    user_router.message.middleware(InnerLoadCartMiddleware())
    user_router.message.middleware(InnerTimingMiddleware())

    dp.include_router(admin_router)
    dp.include_router(user_router)
    return dp


# ═══════════════════════════════════════════════════════════════════════
# pytest: ishga tushirish tartibini ro'yxat orqali isbotlash
# ═══════════════════════════════════════════════════════════════════════
import pytest


class RecordingMiddleware(BaseMiddleware):
    # Sinov uchun: har bir bosqichni umumiy ro'yxatga yozib boradi.

    def __init__(self, name: str, trace: list):
        self.name = name
        self.trace = trace

    async def __call__(self, handler, event, data):
        self.trace.append(f"-> {self.name}")
        result = await handler(event, data)
        self.trace.append(f"<- {self.name}")
        return result


@pytest.mark.asyncio
async def test_middleware_order_is_onion_shaped():
    trace: list[str] = []
    router = Router(name="test")
    router.update.outer_middleware(RecordingMiddleware("OUTER-1", trace))
    router.update.outer_middleware(RecordingMiddleware("OUTER-2", trace))
    router.message.middleware(RecordingMiddleware("INNER-1", trace))
    router.message.middleware(RecordingMiddleware("INNER-2", trace))

    @router.message(Command("ping"))
    async def handler(message: Message) -> None:
        trace.append("HANDLER")

    dp = Dispatcher()
    dp.include_router(router)

    # _build_fake_command_update — 6-darsda ("Botlarni testlash") yozilgan
    # yordamchi funksiya: minimal Update/Message obyektini qo'lda quradi.
    fake_update = _build_fake_command_update("/ping")
    await dp.feed_update(bot=None, update=fake_update)

    assert trace == [
        "-> OUTER-1", "-> OUTER-2", "-> INNER-1", "-> INNER-2",
        "HANDLER",
        "<- INNER-2", "<- INNER-1", "<- OUTER-2", "<- OUTER-1",
    ]
