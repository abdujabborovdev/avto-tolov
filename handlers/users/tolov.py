from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    LabeledPrice,
    PreCheckoutQuery,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from utils.db_api.create_user import *
from states.tolov_qilish import Tolov_qilish
from data.config import *
from handlers.users.check import chek_text, chek_image

router = Router()

MIN_SUMMA = 1000
MAX_SUMMA = 10_000_000
CHANNEL_ID = '-1004365925735'


@router.callback_query(F.data == "tolov_qilish")
async def callback(message: CallbackQuery, state: FSMContext):
    await state.set_state(Tolov_qilish.summa)
    await message.message.edit_text(
        f"""<b>💵 Balansizni necha so'mga to'ldirmoqchisiz?
📰 Minimal miqdor: 1 000 so'm</b>""",
        parse_mode='HTML',
    )


@router.message(Tolov_qilish.summa)
async def summa(message: Message, state: FSMContext):
    text = (message.text or "").replace(" ", "")

    if not text.isdigit():
        await message.answer("⚠️ Xatolik: Iltimos, faqat raqam ko'rinishida kiriting (masalan: 1000)")
        return

    user_summa = int(text)

    if user_summa < MIN_SUMMA:
        await message.answer("⚠️ To'lov miqdori minimaldan kam, minimal 1000 so'm kirita olasiz")
        return

    if user_summa > MAX_SUMMA:
        await message.answer(f"⚠️ Maksimal miqdor: {MAX_SUMMA:,} so'm".replace(",", " "))
        return

    await state.clear()
    telegram_id = message.from_user.id

    await message.answer_invoice(
        title="Balansni to'ldirish",
        description=f"Balansingizga {user_summa:,} so'm qo'shiladi".replace(",", " "),
        payload=f"topup:{telegram_id}:{user_summa}",
        provider_token=CLICK_PROVIDER_TOKEN,
        currency="UZS",
        prices=[LabeledPrice(label="Balans", amount=user_summa * 100)],
    )


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    try:
        kind, uid, summa_str = query.invoice_payload.split(":")
        valid = (
            kind == "topup"
            and int(uid) == query.from_user.id
            and int(summa_str) * 100 == query.total_amount
            and query.currency == "UZS"
        )
    except ValueError:
        valid = False

    if not valid:
        await query.answer(ok=False, error_message="To'lov ma'lumotlari noto'g'ri.")
        return

    async with async_session() as session:
        result = await session.execute(select(User).filter(User.id == query.from_user.id))
        if not result.scalar_one_or_none():
            await query.answer(ok=False, error_message="Avval /start bosib ro'yxatdan o'ting.")
            return

    await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    sp = message.successful_payment

    _, uid, _ = sp.invoice_payload.split(":")
    telegram_id = int(uid)
    summa = sp.total_amount // 100

    order_id = sp.provider_payment_charge_id or sp.telegram_payment_charge_id

    user_found = True
    new_balance = 0

    async with async_session() as session:
        result = await session.execute(
            select(Transaction).filter(Transaction.order_id == order_id)
        )
        if result.scalar_one_or_none():
            return

        result = await session.execute(select(User).filter(User.id == telegram_id))
        user = result.scalar_one_or_none()

        if user:
            tranzaksiya = Transaction(
                order_id=order_id,
                telegram_id=telegram_id,
                summa=summa,
                holat="paid",
            )
            current_hisob = int(user.hisob) if user.hisob else 0
            user.hisob = current_hisob + summa
            new_balance = user.hisob
        else:
            user_found = False
            tranzaksiya = Transaction(
                order_id=order_id,
                telegram_id=telegram_id,
                summa=summa,
                holat="user_not_found",
            )

        session.add(tranzaksiya)

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            return

    if not user_found:
        for admin_id in ADMINS:
            try:
                await message.bot.send_message(
                    admin_id,
                    f"⚠️ <b>To'lov o'tdi, lekin user bazada topilmadi!</b>\n\n"
                    f"👤 ID: <code>{telegram_id}</code>\n"
                    f"💵 Summa: <b>{summa} so'm</b>\n"
                    f"🆔 Order ID: <code>{order_id}</code>",
                    parse_mode="HTML",
                )
            except Exception:
                pass
        await message.answer(
            "⚠️ To'lov qabul qilindi, lekin hisobingiz topilmadi.\n\n"
            "<b>Xatolik roy bersa:</b> @biloliddinabdujabborov",
            parse_mode="HTML",
        )
        return

    try:
        await message.answer_photo(
            chek_image(order_id, telegram_id, summa, new_balance),
            caption=f"✅ To'lov muvaffaqiyatli tasdiqlandi! {summa} so'm hisobingizga qo'shildi.",
        )
    except Exception as e:
        print(f"Chek da xatolik: {e}")
        await message.answer(chek_text(order_id, telegram_id, summa, new_balance), parse_mode="HTML")

    tid = str(telegram_id)
    masked_id = tid[:2] + '*' * max(len(tid) - 4, 0) + tid[-2:]

    try:
        await message.bot.send_message(
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
            await message.bot.send_message(
                admin_id,
                f"💰 <b>Yangi to'lov amalga oshirildi!</b>\n\n"
                f"👤 Foydalanuvchi ID: <code>{telegram_id}</code>\n"
                f"💵 Summa: <b>{summa} so'm</b>\n"
                f"🆔 Order ID: <code>{order_id}</code>",
                parse_mode="HTML",
            )
        except Exception:
            pass
