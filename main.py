# review_flow.py -- Mini App + initData + Payments
from aiogram import Bot, F, Router
from aiogram.types import LabeledPrice, Message, PreCheckoutQuery

router = Router()

# Security modulidan xavfsizlik funksiyasini import qilish
from security import verify_init_data


def get_real_price(product_id: str) -> int:
    """Serverdagi haqiqiy narxni qaytaradi (tiyinda/tijorat birligida).
    Masalan: 50,000 UZS = 5000000 (agar provayder tiyinda qabul qilsa)
    """
    prices = {"prod_1": 5000000, "prod_2": 10000000}
    return prices.get(product_id, 0)


def mark_paid_in_db(payload: str, charge_id: str) -> None:
    """Ma'lumotlar bazasida buyurtmani to'langan deb belgilash."""
    # DB logika bu yerga yoziladi
    pass


async def handle_mini_app_order(
    bot: Bot, chat_id: int, init_data: str, product_id: str
) -> None:
    # 1. Mini App'dan kelgan Telegram xavfsizlik ma'lumotlarini tekshirish
    user = verify_init_data(init_data, bot_token=bot.token)
    if user is None:
        raise PermissionError("initData yaroqsiz -- so'rov rad etildi")

    # 2. Narxni Mijozdan (Frontend) emas, qat'iy Server bazasidan olish
    price = get_real_price(product_id)
    if price <= 0:
        raise ValueError("Mahsulot narxi noto'g'ri")

    # 3. aiogram 3.x uchun LabeledPrice obyektini yaratish
    prices = [LabeledPrice(label="Narx", amount=price)]

    # 4. Invoys yuborish
    await bot.send_invoice(
        chat_id=chat_id,
        title="Buyurtma",
        description=f"Mahsulot #{product_id}",
        payload=f"order:{user['id']}:{product_id}",
        provider_token="PROVIDER_TOKEN",  # BotFather'dan olingan token
        currency="UZS",
        prices=prices,
    )


@router.pre_checkout_query()
async def confirm_pre_checkout(pre_checkout_query: PreCheckoutQuery) -> None:
    # Telegram to'lovni amalga oshirishdan oldin 10 soniya ichida tasdiq so'raydi
    # Bu yerda ombor omborida mahsulot bor-yo'qligini qayta tekshirish mumkin
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def mark_order_paid(message: Message) -> None:
    # To'lov muvaffaqiyatli amalga oshirilgach, DB'ga yozish va foydalanuvchiga xabar berish
    payment_info = message.successful_payment
    payload = payment_info.invoice_payload
    charge_id = payment_info.telegram_payment_charge_id

    mark_paid_in_db(payload, charge_id=charge_id)

    await message.answer("To'lovingiz muvaffaqiyatli qabul qilindi! Rahmat.")