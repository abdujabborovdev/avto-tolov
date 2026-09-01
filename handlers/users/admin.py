
from aiogram import Router, F

from data.config import *
from keyboards.default.admin import admin_k
from sqlalchemy import select, delete, func
from utils.db_api.create_user import Numbers_list, async_session, Transaction, User, Order_numbers,SecretApiKey
import aiohttp
from states.add_mon import Suma_qosh, AdminSearchState, NumberSearchState, TransactionSearchState
from aiogram.fsm.context import FSMContext
from states.send_message import *
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from utils.db_api.create_user import SecretApiKey  # Model joylashgan yo'l
router = Router()

SEENSMS_KEY = SEENSMS_KEY
ADMINS = ADMINS


@router.message(F.text == '/secret')
async def admin(message: Message):
    if message.from_user.id in ADMINS:
        await message.answer(f"""Admin panelga hush kelibsiz""", reply_markup=admin_k)
    else:
        await message.answer("Siz admin emasiz")


@router.message(F.text == 'Nomerlarni yangilash')
async def yangilash(message: Message):
    if message.from_user.id in ADMINS:

        URL = 'https://seensms.uz/api/v1'

        async with aiohttp.ClientSession() as sess:
            async with sess.post(URL, data={
                'key': f'{SEENSMS_KEY}',
                'action': 'accounts_countries',
            }) as r:
                dat = await r.json()

        async with async_session() as session:
            await session.execute(delete(Numbers_list))
            await session.commit()
            try:
                for i in dat:
                    price = i['price'] * 1.4
                    new_number = Numbers_list(country=i['country'], price=price)
                    session.add(new_number)
                    await session.commit()
                await message.answer(f"""Nomerlar royhati yangilandi""")

            except Exception as e:
                await message.answer(f"""Xatolik - {e}""")


@router.message(F.text == "Tolovlar tarixi")
async def tarix_t(message: Message):
    if message.from_user.id in ADMINS:
        async with async_session() as session:
            result = await session.execute(select(func.count()).select_from(Transaction))
            total_transactions = result.scalar_one()

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text="🔍 Tranzaksiya ID orqali qidirish",
                    callback_data="search_transaction",
                )
            ]]
        )

        await message.answer(
            f"💳 <b>Jami to'lovlar tarixi soni:</b> {total_transactions} ta",
            reply_markup=keyboard,
            parse_mode="HTML",
        )


@router.callback_query(F.data == "search_transaction")
async def ask_transaction_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Qidirmoqchi bo'lgan to'lovning <b>ID</b> (order_id) raqamini kiriting:",
        parse_mode="HTML",
    )
    await state.set_state(TransactionSearchState.waiting_for_transaction_id)
    await callback.answer()


@router.message(TransactionSearchState.waiting_for_transaction_id)
async def find_transaction_by_id(message: Message, state: FSMContext):
    trans_id = message.text.strip()  # Matnligicha qabul qilamiz

    async with async_session() as session:
        result = await session.execute(select(Transaction).filter_by(order_id=trans_id))
        tranzaksiya = result.scalar_one_or_none()

    if tranzaksiya:
        matn = (
            f"✅ <b>To'lov topildi:</b>\n\n"
            f"🆔 <b>ID (Order ID):</b> {tranzaksiya.order_id}\n"
            f"💰 <b>Summa:</b> {tranzaksiya.summa}\n"
            f"📊 <b>Status (Holat):</b> {tranzaksiya.holat}\n"
            f"⏳ <b>Vaqti:</b> {tranzaksiya.vaqti}\n"
            f"👤 <b>Telegram ID (Owner):</b> {tranzaksiya.telegram_id}"
        )
    else:
        matn = f"❌ <b>{trans_id}</b> ID raqamli to'lov topilmadi."

    await message.answer(matn, parse_mode="HTML")
    await state.clear()


@router.message(F.text == 'Foydalanuvchilar')
async def foydalanuvchilar(message: Message):
    if message.from_user.id in ADMINS:
        async with async_session() as session:
            result = await session.execute(select(func.count()).select_from(User))
            user_count = result.scalar_one()

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text='🔍 ID orqali qidirish', callback_data='search_user'
                )
            ]]
        )

        await message.answer(
            f'👥 <b>Jami foydalanuvchilar soni:</b> {user_count} ta',
            reply_markup=keyboard,
            parse_mode='HTML',
        )


@router.callback_query(F.data == 'search_user')
async def ask_user_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Qidirmoqchi bo'lgan foydalanuvchining <b>ID</b> raqamini kiriting:",
        parse_mode='HTML',
    )
    await state.set_state(AdminSearchState.waiting_for_user_id)
    await callback.answer()


@router.message(AdminSearchState.waiting_for_user_id)
async def find_user_by_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('❌ Iltimos, faqat raqamlardan iborat ID kiriting!')
        return

    user_id = int(message.text)

    async with async_session() as session:
        result = await session.execute(select(User).filter_by(id=user_id))
        user = result.scalar_one_or_none()

    if user:
        matn = (
            f'✅ <b>Foydalanuvchi topildi:</b>\n\n'
            f'🆔 <b>ID:</b> {user.id}\n'
            f'👤 <b>Username:</b> @{user.username}\n'
            f'🪪 <b>Ism:</b> {user.name}\n'
            f'💳 <b>Balans:</b> {user.hisob} so\'m'
        )
    else:
        matn = f"❌ <b>{user_id}</b> ID raqamli foydalanuvchi topilmadi."

    await message.answer(matn, parse_mode='HTML')
    await state.clear()


@router.message(F.text == 'Nomerlar royhati')
async def foydalanuvchilar(message: Message):
    if message.from_user.id in ADMINS:
        async with async_session() as session:
            result = await session.execute(select(Numbers_list))
            royhat = result.scalars().all()

        matn = f"<b>Ro'yxati:</b>\n\n"

        for u in royhat:
            matn += f"ID: {u.id}| {u.country} | {u.price}\n"
        await message.answer(matn, parse_mode='HTML')


@router.message(F.text == 'Nomerlar tarixi')
async def nomerlar_tarixi(message: Message):
    if message.from_user.id in ADMINS:
        async with async_session() as session:
            result = await session.execute(select(func.count()).select_from(Order_numbers))
            total_numbers = result.scalar_one()

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text='🔍 Nomer ID orqali qidirish', callback_data='search_number'
                )
            ]]
        )

        await message.answer(
            f'📦 <b>Jami sotib olingan/tarixdagi nomerlar soni:</b> {total_numbers} ta',
            reply_markup=keyboard,
            parse_mode='HTML',
        )


@router.callback_query(F.data == 'search_number')
async def ask_number_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Qidirmoqchi bo'lgan nomerning <b>ID</b> raqamini kiriting:",
        parse_mode='HTML',
    )
    await state.set_state(NumberSearchState.waiting_for_number_id)
    await callback.answer()


@router.message(NumberSearchState.waiting_for_number_id)
async def find_number_by_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('❌ Iltimos, faqat raqamlardan iborat ID kiriting!')
        return

    num_id = int(message.text)

    async with async_session() as session:
        result = await session.execute(select(Order_numbers).filter_by(id=num_id))
        item = result.scalar_one_or_none()

    if item:
        matn = (
            f'✅ <b>Nomer topildi:</b>\n\n'
            f'🆔 <b>ID:</b> {item.id}\n'
            f'🌍 <b>Davlat (Country):</b> {item.country}\n'
            f'👤 <b>Egasi (Owner):</b> {item.owner_number}\n'
            f'📞 <b>Nomer:</b> {item.number}\n'
            f'📊 <b>Status:</b> {item.status}\n'
            f'🔑 <b>Kod:</b> {item.kod}\n'
            f'🛡 <b>Parol 2:</b> {item.pas2}'
        )
    else:
        matn = f"❌ <b>{num_id}</b> ID raqamli nomer topilmadi."

    await message.answer(matn, parse_mode='HTML')
    await state.clear()


@router.message(F.text == 'Hisobiga qoshish')
async def foydalanuvchilar(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.set_state(Suma_qosh.tg_idsi)
        await message.answer(f"Idsini kiriting")


@router.message(Suma_qosh.tg_idsi)
async def foydalanuvchilar(message: Message, state: FSMContext):
    user_id = message.text

    async with async_session() as session:
        result = await session.execute(select(User).filter(User.id == user_id))
        useri = result.scalar_one_or_none()

    if useri:
        await state.update_data(tg_idsi=user_id)
        await message.answer(f"qancha suma kirit moqchisiz oldingi sumasi {useri.hisob}")
        await state.set_state(Suma_qosh.summa)
    else:
        await message.answer("Bunday user yoq qayta kiriting")


@router.message(Suma_qosh.summa)
async def foydalanuvchilar(message: Message, state: FSMContext):
    text = message.text.strip()

    try:
        suma = int(text)
    except ValueError:
        await message.answer(
            "❌ Iltimos, faqat raqam kiriting!\n(Masalan, qo'shish uchun: <b>5000</b>, ayirish uchun: <b>-5000</b>)",
            parse_mode="HTML")
        return

    data = await state.get_data()
    user_id = data.get("tg_idsi")

    async with async_session() as session:
        result = await session.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            await message.answer("❌ Bu ID bo'yicha foydalanuvchi bazadan topilmadi!")
            await state.clear()
            return

        try:
            current_hisob = int(user.hisob) if user.hisob is not None else 0
        except (ValueError, TypeError):
            current_hisob = 0

        user.hisob = current_hisob + suma
        await session.commit()

        if suma < 0:
            await message.answer(
                f"✅ Muvaffaqiyatli! Foydalanuvchi hisobidan <b>{abs(suma)}</b> so'm ayrildi.\n💳 Yangi balans: <b>{user.hisob}</b> so'm",
                parse_mode="HTML")
        else:
            await message.answer(
                f"✅ Muvaffaqiyatli! Foydalanuvchi hisobiga <b>{suma}</b> so'm qo'shildi.\n💳 Yangi balans: <b>{user.hisob}</b> so'm",
                parse_mode="HTML")

    await state.clear()


from keyboards.default.cencel import cencel_but


@router.message(F.text == "Habar yuborish")
async def send_message(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.set_state(Send_m.mess)
        await message.answer(f"Userlarga yubormoqchi bolgan xabaringizni kiriting ✍🏻", reply_markup=cencel_but)


@router.message(F.text == "Bekor qilish ❌")
async def send_message(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.clear()
        await message.answer("Bekor qilinid ✅", reply_markup=admin_k)


@router.message(Send_m.mess)
async def send_message(message: Message, state: FSMContext):

    async with async_session() as session:
        result = await session.execute(select(User.id))
        user_id_list = result.scalars().all()

    secces = 0
    blocked = 0
    for user_id in user_id_list:
        try:
            await message.copy_to(chat_id=user_id)
            secces += 1
        except Exception as e:
            blocked += 1
            print(f"{user_id}: {e}")

    await state.clear()

    await message.answer(
        f"Xabaringiz muvafiyaqiyatlik yuborilindi jami yuborilinganlar - {secces}, yuborilmadi - {blocked}",
        reply_markup=admin_k)





from contextlib import asynccontextmanager
from math import ceil

from aiogram import Router, F
from aiogram.filters import Filter
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, func, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_api.create_user import SecretApiKey
from utils.db_api.create_user import async_session  # sessionmaker (async_sessionmaker)


PAGE_SIZE = 10
ADMIN_IDS = [6917400767]  # <-- o'zingizning admin ID'laringizni kiriting



class IsAdmin(Filter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return event.from_user.id in ADMIN_IDS



@asynccontextmanager
async def get_session(data: dict):

    session: AsyncSession | None = data.get("session")
    if session is not None:
        yield session
    else:
        async with async_session() as new_session:
            yield new_session


# ==========================================================
# CALLBACK DATA FACTORY'LARI
# ==========================================================
class ApiKeyListCB(CallbackData, prefix="apk_list"):
    page: int


class ApiKeyDetailCB(CallbackData, prefix="apk_detail"):
    id: int
    page: int


class ApiKeyDeleteCB(CallbackData, prefix="apk_del"):
    id: int
    page: int


class ApiKeyToggleCB(CallbackData, prefix="apk_toggle"):
    id: int
    page: int


# ==========================================================
# YORDAMCHI FUNKSIYALAR
# ==========================================================
async def get_total_pages(session: AsyncSession) -> int:
    total = (await session.execute(select(func.count()).select_from(SecretApiKey))).scalar_one()
    return max(1, ceil(total / PAGE_SIZE))


async def build_list_keyboard(session: AsyncSession, page: int):
    total_pages = await get_total_pages(session)
    page = max(0, min(page, total_pages - 1))

    stmt = (
        select(SecretApiKey)
        .order_by(SecretApiKey.id)
        .offset(page * PAGE_SIZE)
        .limit(PAGE_SIZE)
    )
    keys = (await session.execute(stmt)).scalars().all()

    builder = InlineKeyboardBuilder()
    for key in keys:
        status_emoji = "🔴" if key.is_blocked else "🟢"
        builder.button(
            text=f"{status_emoji} #{key.id} | {key.user_telegram_id}",
            callback_data=ApiKeyDetailCB(id=key.id, page=page).pack(),
        )
    builder.adjust(1)

    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data=ApiKeyListCB(page=page - 1).pack())
        )
    nav_row.append(
        InlineKeyboardButton(text=f"📄 {page + 1}/{total_pages}", callback_data="apk_noop")
    )
    if page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton(text="Oldinga ➡️", callback_data=ApiKeyListCB(page=page + 1).pack())
        )
    builder.row(*nav_row)

    return builder.as_markup(), keys, total_pages


def build_detail_text(key: SecretApiKey) -> str:
    status = "🔴 Bloklangan" if key.is_blocked else "🟢 Faol"
    return (
        f"🔑 <b>API Kalit ma'lumotlari</b>\n\n"
        f"🆔 <b>ID:</b> <code>{key.id}</code>\n"
        f"👤 <b>User ID:</b> <code>{key.user_telegram_id}</code>\n"
        f"🔐 <b>Secret Key:</b> <code>{key.secret_api_key}</code>\n"
        f"📊 <b>Holati:</b> {status}"
    )


def build_detail_keyboard(key: SecretApiKey, page: int):
    builder = InlineKeyboardBuilder()
    toggle_text = "🟢 Blokdan yechish" if key.is_blocked else "🔴 Bloklash"
    builder.button(text=toggle_text, callback_data=ApiKeyToggleCB(id=key.id, page=page).pack())
    builder.button(text="🗑 Kalitni o'chirish", callback_data=ApiKeyDeleteCB(id=key.id, page=page).pack())
    builder.button(text="⬅️ Ro'yxatga qaytish", callback_data=ApiKeyListCB(page=page).pack())
    builder.adjust(1)
    return builder.as_markup()


# ==========================================================
# 1) "Apilar" — ro'yxatni chiqarish
# ==========================================================
@router.message(IsAdmin(), F.text == "Apilar")
async def show_api_keys_list(message: Message, **data):
    async with get_session(data) as session:
        keyboard, keys, total_pages = await build_list_keyboard(session, page=0)

        if not keys:
            await message.answer("📭 Hozircha bazada API kalitlar mavjud emas.")
            return

        await message.answer(
            f"🔑 <b>API kalitlar ro'yxati</b> (Jami sahifalar: {total_pages})",
            reply_markup=keyboard,
        )


# ==========================================================
# 2) Sahifalash (Oldinga / Orqaga)
# ==========================================================
@router.callback_query(IsAdmin(), ApiKeyListCB.filter())
async def paginate_api_keys(call: CallbackQuery, callback_data: ApiKeyListCB, **data):
    async with get_session(data) as session:
        keyboard, keys, total_pages = await build_list_keyboard(session, page=callback_data.page)

        if not keys:
            await call.answer("📭 Bu sahifada kalitlar topilmadi.", show_alert=True)
            return

        await call.message.edit_text(
            f"🔑 <b>API kalitlar ro'yxati</b> (Jami sahifalar: {total_pages})",
            reply_markup=keyboard,
        )
        await call.answer()


@router.callback_query(F.data == "apk_noop")
async def noop_handler(call: CallbackQuery):
    await call.answer()


# ==========================================================
# 3) Bitta kalit haqida batafsil ma'lumot
# ==========================================================
@router.callback_query(IsAdmin(), ApiKeyDetailCB.filter())
async def show_api_key_detail(call: CallbackQuery, callback_data: ApiKeyDetailCB, **data):
    async with get_session(data) as session:
        key = await session.get(SecretApiKey, callback_data.id)

        if key is None:
            await call.answer("❌ Bu kalit topilmadi (o'chirilgan bo'lishi mumkin).", show_alert=True)
            return

        await call.message.edit_text(
            build_detail_text(key),
            reply_markup=build_detail_keyboard(key, callback_data.page),
        )
        await call.answer()


# ==========================================================
# 4) Kalitni o'chirish
# ==========================================================
@router.callback_query(IsAdmin(), ApiKeyDeleteCB.filter())
async def delete_api_key(call: CallbackQuery, callback_data: ApiKeyDeleteCB, **data):
    async with get_session(data) as session:
        key = await session.get(SecretApiKey, callback_data.id)

        if key is None:
            await call.answer("❌ Bu kalit allaqachon o'chirilgan.", show_alert=True)
            return

        await session.execute(sa_delete(SecretApiKey).where(SecretApiKey.id == callback_data.id))
        await session.commit()

        await call.answer("🗑 Kalit muvaffaqiyatli o'chirildi.", show_alert=True)

        # Ro'yxatga qaytarish
        keyboard, keys, total_pages = await build_list_keyboard(session, page=callback_data.page)

        if not keys and callback_data.page > 0:
            # Sahifa bo'sh qolsa, oldingi sahifaga qaytaramiz
            keyboard, keys, total_pages = await build_list_keyboard(session, page=callback_data.page - 1)

        if not keys:
            await call.message.edit_text("📭 Hozircha bazada API kalitlar mavjud emas.")
            return

        await call.message.edit_text(
            f"🔑 <b>API kalitlar ro'yxati</b> (Jami sahifalar: {total_pages})",
            reply_markup=keyboard,
        )



@router.callback_query(IsAdmin(), ApiKeyToggleCB.filter())
async def toggle_block_api_key(call: CallbackQuery, callback_data: ApiKeyToggleCB, **data):
    async with get_session(data) as session:
        key = await session.get(SecretApiKey, callback_data.id)

        if key is None:
            await call.answer("❌ Bu kalit topilmadi.", show_alert=True)
            return

        key.is_blocked = not key.is_blocked
        await session.commit()
        await session.refresh(key)

        status_text = "bloklandi 🔴" if key.is_blocked else "blokdan yechildi 🟢"
        await call.answer(f"✅ Kalit {status_text}.")

        await call.message.edit_text(
            build_detail_text(key),
            reply_markup=build_detail_keyboard(key, callback_data.page),
        )