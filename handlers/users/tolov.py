
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import time
from sqlalchemy import select
from utils.db_api.create_user import *  # async_session, User, Transaction va h.k.
import aiohttp
from states.tolov_qilish import Tolov_qilish
from keyboards.inline.tolov import *
from data.config import INPAY_TOKEN, INPAY_ID, ADMINS

router = Router()
_cached_bearer = None
_cashed_time = 0


async def cached_bearer():
    global _cached_bearer, _cashed_time
    hozirgi = time.time()
    yigirma_soat = 20 * 3600

    if not _cached_bearer or (hozirgi - _cashed_time) >= yigirma_soat:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(
                "https://inpay.uz/api/v1/authorization/",
                params={"merchant_id": INPAY_ID, "merchant_token": INPAY_TOKEN},
                headers={"Accept": "application/json"},
                timeout=10,
            ) as r:
                data = await r.json()
        if not data.get("success"):
            raise RuntimeError(f"Auth xatosi: {data}")

        _cached_bearer = data.get("bearer_token")
        _cashed_time = hozirgi

    return _cached_bearer


@router.callback_query(F.data == "tolov_qilish")
async def callback(message: CallbackQuery, state: FSMContext):
    await state.set_state(Tolov_qilish.summa)
    await message.message.edit_text(f"""<b>💵 Balansizni necha so'mga to'ldirmoqchisiz? 
📰 Minimal miqdor: 1 000 so'm</b>""", parse_mode='HTML')


@router.message(Tolov_qilish.summa)
async def summa(message: Message, state: FSMContext):
    try:
        user_summa = int(message.text)
        if user_summa < 1000:
            await message.answer("""⚠️ To'lov miqdori minimaldan kam, minimal 1000 so'm kirita olasiz""")
            return
        await state.update_data(summa=user_summa)
    except ValueError:
        await message.answer("⚠️ Xatolik: Iltimos, faqat raqam ko'rinishida kiriting (masalan: 10000)")
        return

    data = await state.get_data()
    summa = data.get("summa")
    await state.clear()

    bearer_token = await cached_bearer()
    payload = {
        "merchant_id": INPAY_ID,
        "token": INPAY_TOKEN,
        "amount": summa,
        "description": f"{message.from_user.id}",
    }

    async with aiohttp.ClientSession() as sess:
        async with sess.post(
            "https://inpay.uz/api/v1/create/",
            json=payload,
            headers={"Authorization": f"Bearer {bearer_token}"},
            timeout=15,
        ) as r:
            data = await r.json()
    url = data.get('pay_url')
    tolov_id = data.get('order_id')
    telegram_id = message.from_user.id

    keyboard_tolov = get_payment_keyboard(pay_url=url, order_id=tolov_id, telegram_id=telegram_id, summasi=summa)

    await message.answer(f"""⚠️ To'lov to'langandan keyin <b>✅ To'lov qildim</b> tugmasini bosing, bot balansiga avtomatik tashlab beriladi. 

<b>💳 To'lov midori:</b> {summa} so'm

<b>Buyurtma raqami:</b> <code>{tolov_id}</code>

<b>Xatolik roy bersa:</b> @itredr""", reply_markup=keyboard_tolov, parse_mode='HTML')

    async with async_session() as session:
        new_order_pay = Transaction(order_id=tolov_id, telegram_id=telegram_id, summa=summa)
        session.add(new_order_pay)
        await session.commit()


active_checks = set()


@router.callback_query(F.data.startswith("check_pay"))
async def check_pay(call: CallbackQuery):
    user_id = call.from_user.id

    if user_id in active_checks:
        await call.answer("⏳ So'rovingiz bajarilmoqda, biroz kuting...", show_alert=False)
        return

    active_checks.add(user_id)

    try:
        await call.answer()

        data_parts = call.data.split(":")
        if len(data_parts) < 4:
            await call.message.answer("⚠️ Xatolik: Ma'lumotlar yetarli emas.\n\n<b>Xatolik roy bersa:</b> @itredr",
                                      parse_mode='HTML')
            return

        order_id = data_parts[1]
        telegram_id = int(data_parts[2])
        summa = int(data_parts[3])

        if not order_id:
            await call.message.answer("❌ Order ID topilmadi.\n\n<b>Xatolik roy bersa:</b> @itredr", parse_mode='HTML')
            return

        url = f"https://inpay.uz/api/v1/transactions/?order_id={order_id}"
        headers = {"Accept": "application/json"}

        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, headers=headers) as response:
                data = await response.json()

        try:
            status = data.get("data", {}).get("status") or data.get("status", "pending")
        except Exception:
            status = "pending"

        async with async_session() as session:
            result = await session.execute(
                select(Transaction).filter(Transaction.order_id == order_id)
            )
            tranzaksiya = result.scalar_one_or_none()

            if tranzaksiya and tranzaksiya.holat == "success":
                await call.message.answer(
                    "✅ Bu to'lov muvaffaqiyatli amalga oshirilgan!\n\n<b>Xatolik roy bersa:</b> @itredr",
                    parse_mode='HTML')
                return

            if not tranzaksiya:
                tranzaksiya = Transaction(
                    order_id=order_id,
                    telegram_id=telegram_id,
                    summa=summa,
                    holat=status
                )
                session.add(tranzaksiya)
            else:
                tranzaksiya.holat = status

            await session.commit()

            if status == "success":
                result = await session.execute(select(User).filter(User.id == telegram_id))
                user = result.scalar_one_or_none()

                if user:
                    if tranzaksiya.holat == 'success':
                        pass

                    current_hisob = int(user.hisob) if user.hisob else 0
                    user.hisob = current_hisob + summa
                    tranzaksiya.holat = 'success'
                    await session.commit()

                    masked_id = (str(telegram_id)[:2] + '*' * (len(str(telegram_id)) - 4) + str(telegram_id)[-2:])
                    CHANNEL_ID = '-1004365925735'

                    try:
                        await call.bot.send_message(
                            CHANNEL_ID,
                            text=(
                                f'🔔 <b>Hisob toldirilindi</b>\n\n'
                                f"👤 Foydalanuvchi ID: <code>{masked_id}</code>\n"
                                f"💵 Summa: <b>{summa} so'm</b>\n"
                            ),
                            parse_mode='HTML',
                        )
                    except Exception as e:
                        print(f'Kanalga yuborishda xatolik: {e}')

                    for admin_id in ADMINS:
                        try:
                            await call.bot.send_message(
                                admin_id,
                                f"💰 <b>Yangi to'lov amalga oshirildi!</b>\n\n"
                                f"👤 Foydalanuvchi ID: <code>{telegram_id}</code>\n"
                                f"💵 Summa: <b>{summa} so'm</b>\n"
                                f"🆔 Order ID: <code>{order_id}</code>",
                                parse_mode="HTML"
                            )
                        except Exception:
                            pass

                    await call.message.edit_text(
                        f"✅ To'lov muvaffaqiyatli tasdiqlandi! {summa} so'm hisobingizga qo'shildi.")
                else:
                    await call.message.answer("⚠️ Siz bazadan topilmadingiz.\n\n<b>Xatolik roy bersa:</b> @itredr",
                                              parse_mode='HTML')

            elif status == "pending":
                await call.answer("⏳ To'lov hali amalga oshirilmagan (Kutilmoqda).", show_alert=False)
            elif status == "failed":
                await call.answer("❌ To'lov muvaffaqiyatsiz yakunlandi.\n\n<b>Xatolik roy bersa:</b> @itredr",
                                  parse_mode='HTML', show_alert=False)
            elif status == "cancelled":
                await call.answer("🚫 To'lov bekor qilindi.\n\n<b>Xatolik roy bersa:</b> @itredr", parse_mode='HTML',
                                  show_alert=False)
            else:
                await call.answer(f"ℹ️ To'lov holati: {status}\n\n<b>Xatolik roy bersa:</b> @itredr",
                                  parse_mode='HTML', show_alert=False)

            await session.commit()

    finally:
        active_checks.discard(user_id)