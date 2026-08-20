from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import time
from utils.db_api.create_user import *
import requests
from states.tolov_qilish import Tolov_qilish
import data
from keyboards.inline.tolov import *
from data.config import INPAY_TOKEN, INPAY_ID

router = Router()
_cached_bearer = None
_cashed_time = 0


async def cached_bearer():
    global _cached_bearer, _cashed_time
    hozirgi = time.time()
    yigirma_soat = 20 * 3600

    if not _cached_bearer or (hozirgi - _cashed_time) >= yigirma_soat:
        r = requests.get(
            "https://inpay.uz/api/v1/authorization/",
            params={"merchant_id": INPAY_ID, "merchant_token": INPAY_TOKEN},
            headers={"Accept": "application/json"},
            timeout=10,
        )

        data = r.json()
        if not data.get("success"):
            raise RuntimeError(f"Auth xatosi: {data}")

        _cached_bearer = data["bearer_token"]
        _cashed_time = hozirgi  # <-- Xatolik to'g'irlandi (_time_token emas, _cashed_time)

    return _cached_bearer


@router.callback_query(F.data == "tolov_qilish")
async def callback(message: CallbackQuery, state: FSMContext):
    await state.set_state(Tolov_qilish.summa)
    await message.message.answer("Qanchaga hisobingizni toldirmoqchisiz? Matn ko'rinishida yuboring")


@router.message(Tolov_qilish.summa)
async def summa(message: Message, state: FSMContext):
    try:
        user_summa = int(message.text)
        await state.update_data(summa=user_summa)
    except ValueError:
        await message.answer("⚠️ Xatolik: Iltimos, faqat raqam ko'rinishida kiriting (masalan: 10000)")
        return  # <-- RETURN qo'shildi: agar xato bo'lsa, kod pastga tushib ketmaydi!

    data = await state.get_data()
    summa = data.get("summa")
    await state.clear()

    await message.answer(f"Kiritilgan summa: {summa} so'm qabul qilindi. To'lov havolasi yaratilmoqda...")

    bearer_token = await cached_bearer()
    payload = {
        "merchant_id": INPAY_ID,
        "token": INPAY_TOKEN,
        "amount": summa,
        "description": f"{message.from_user.id}",
    }

    r = requests.post(
        "https://inpay.uz/api/v1/create/",
        json=payload,
        headers={"Authorization": f"Bearer {bearer_token}"},
        timeout=15,
    )

    data = r.json()
    url = data['pay_url']
    tolov_id = data['order_id']
    telegram_id = message.from_user.id

    keyboard_tolov = get_payment_keyboard(pay_url=url, order_id=tolov_id, telegram_id=telegram_id, summasi=summa)
    await message.answer(f"Buyurtma raqami: {data['order_id']}", reply_markup=keyboard_tolov)


@router.callback_query(F.data.startswith("check_pay"))
async def check_pay(call: CallbackQuery):
    await call.answer()

    data_parts = call.data.split(":")
    if len(data_parts) < 4:
        await call.message.answer("⚠️ Xatolik: Ma'lumotlar yetarli emas.")
        return

    order_id = data_parts[1]
    telegram_id = int(data_parts[2])
    summa = int(data_parts[3])

    if not order_id:
        await call.message.answer("⚠️ Order ID topilmadi.")
        return

    url = f"https://inpay.uz/api/v1/transactions/?order_id={order_id}"
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)
    data = response.json()

    try:
        status = data.get("data", {}).get("status") or data.get("status", "pending")
    except Exception:
        status = "pending"

    tranzaksiya = session.get(Transaction, order_id)

    if tranzaksiya:
        if tranzaksiya.holat == "success":
            await call.message.answer("⚠️ Bu to'lov allaqachon muvaffaqiyatli o'tgan!")
            return

        tranzaksiya.holat = status
        session.commit()
    else:
        tranzaksiya = Transaction(
            order_id=order_id,
            telegram_id=telegram_id,
            summa=summa,
            holat=status
        )
        session.add(tranzaksiya)
        session.commit()

    if status == "success":
        user = session.query(User).filter(User.id == telegram_id).first()
        if user:
            current_hisob = int(user.hisob) if user.hisob else 0
            user.hisob = current_hisob + summa
            session.commit()

            await call.message.answer(f"✅ To'lov muvaffaqiyatli tasdiqlandi! {summa} so'm hisobingizga qo'shildi.")
            await call.message.edit_reply_markup(reply_markup=None)
        else:
            await call.message.answer("⚠️ Foydalanuvchi bazadan topilmadi.")

    elif status == "pending":
        await call.message.answer("⏳ To'lov hali amalga oshirilmagan (Kutilmoqda).")
    elif status == "failed":
        await call.message.answer("❌ To'lov muvaffaqiyatsiz yakunlandi.")
    elif status == "cancelled":
        await call.message.answer("🚫 To'lov bekor qilindi.")
    else:
        await call.message.answer(f"ℹ️ To'lov holati: {status}")


