
from aiogram import Router, F

from data.config import *
from keyboards.default.admin import admin_k
from sqlalchemy import select, delete, func
from utils.db_api.create_user import Numbers_list, async_session, Transaction, User, Order_numbers
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


@router.message(F.text == "Apilar")
async def show_api_keys(message: Message, session):
    await send_api_keys_page(message, session, page=0)


async def send_api_keys_page(message_or_callback, session, page: int, edit: bool = False):
    result = await session.execute(select(SecretApiKey))
    keys = result.scalars().all()

    if not keys:
        text = "Bazada hali hech qanday API kalit topilmadi."
        if edit:
            await message_or_callback.message.edit_text(text)
        else:
            await message.answer(text)
        return

    total_keys = len(keys)
    PER_PAGE = 10
    start = page * PER_PAGE
    end = start + PER_PAGE
    current_keys = keys[start:end]

    keyboard = []
    for index, item in enumerate(current_keys, start=start + 1):
        short_key = f"{item.secret_api_key[:10]}..."
        keyboard.append([
            InlineKeyboardButton(
                text=f"{index}. ID: {item.user_telegram_id} | {short_key}",
                callback_data=f"apikey_info:{item.id}",
            )
        ])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"apikey_page:{page - 1}")
        )
    if end < total_keys:
        nav_buttons.append(
            InlineKeyboardButton(text="Keyingisi ➡️", callback_data=f"apikey_page:{page + 1}")
        )

    if nav_buttons:
        keyboard.append(nav_buttons)

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    text = f"📋 **Olingan API kalitlar ro'yxati**\nJami: {total_keys} ta\nSahifa: {page + 1}"

    if edit:
        await message_or_callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    else:
        await message_or_callback.answer(text, reply_markup=markup, parse_mode="Markdown")


@router.callback_query(F.data.startswith("apikey_page:"))
async def paginate_api_keys(call: CallbackQuery, session):
    page = int(call.data.split(":")[1])
    await send_api_keys_page(call, session, page=page, edit=True)
    await call.answer()


@router.callback_query(F.data.startswith("apikey_info:"))
async def api_key_detail(call: CallbackQuery, session):
    key_id = int(call.data.split(":")[1])

    result = await session.execute(select(SecretApiKey).filter(SecretApiKey.id == key_id))
    api_key_obj = result.scalars().first()

    if not api_key_obj:
        await call.answer("Bunday API kalit topilmadi!", show_alert=True)
        return

    info_text = (
        f"🔑 **API Kalit Ma'lumotlari:**\n\n"
        f"🆔 **ID:** `{api_key_obj.id}`\n"
        f"👤 **Telegram User ID:** `{api_key_obj.user_telegram_id}`\n"
        f"🔐 **Secret API Key:** `{api_key_obj.secret_api_key}`"
    )

    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Ro'yxatga qaytish", callback_data="apikey_page:0")]
        ]
    )

    await call.message.edit_text(info_text, reply_markup=back_keyboard, parse_mode="Markdown")
    await call.answer()