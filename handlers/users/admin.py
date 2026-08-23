from calendar import firstweekday
from idlelib import rpc

from aiogram import Router,F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from data.config import *
from keyboards.default.admin import admin_k
from utils.db_api.create_user import Numbers_list, session, Transaction, User, Order_numbers
import aiohttp
from states.add_mon import Suma_qosh

router = Router()

SEENSMS_KEY=SEENSMS_KEY
ADMINS = ADMINS


@router.message(F.text == '/secret')
async def admin(message: Message):
    if message.from_user.id in ADMINS:
        await message.answer(f"""Admin panelga hush kelibsiz""",reply_markup=admin_k)

    else:
        await message.answer("Siz admin emasiz")

@router.message(F.text == 'Nomerlarni yangilash')
async def yangilash(message:Message):
    if message.from_user.id in ADMINS:

        URL = 'https://seensms.uz/api/v1'

        async with aiohttp.ClientSession() as sess:
            async with sess.post(URL, data={
            'key': f'{SEENSMS_KEY}',
            'action': 'accounts_countries',
        }) as r:
             dat = await r.json()

        session.query(Numbers_list).delete()
        session.commit()
        try:
            for i in dat:
                price = i['price'] * 1.2
                new_number = Numbers_list(country=i['country'],price=price)
                session.add(new_number)
                session.commit()
            await message.answer(f"""Nomerlar royhati yangilandi""")

        except Exception as e:
            await message.answer(f"""Xatolik - {e}""")



@router.message(F.text == 'Tolovlar tarixi')
async def tarix_t(message:Message):
    if message.from_user.id in ADMINS:
        tarix = session.query(Transaction).all()
        matn = "<b>💳 To'lovlar tarixi:</b>\n\n"
        for t in tarix:
            matn += f"ID: {t.order_id} | Summa: {t.summa} | Status: {t.holat} | Vaqti {t.vaqti} | Owner : {t.telegram_id}\n"

        await message.answer(matn, parse_mode='HTML')
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from utils.db_api.create_user import User, session  # o'zingizning importlar


@router.message(F.text == 'Foydalanuvchilar')
async def foydalanuvchilar(message: Message):
  if message.from_user.id in ADMINS:
    # Jami foydalanuvchilar sonini sanaymiz
    user_count = session.query(User).count()

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

  user = session.query(User).filter_by(id=user_id).first()

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
  await state.clear()  # Holatni tozalaymiz

@router.message(F.text=='Nomerlar royhati')
async def foydalanuvchilar(message:Message):
    if message.from_user.id in ADMINS:
        royhat = session.query(Numbers_list).all()
        matn = f"<b>Ro'yxati:</b>\n\n"

        for u in royhat:
            matn += f"ID: {u.id}| {u.country} | {u.price}\n"
        await message.answer(matn, parse_mode='HTML')

@router.message(F.text=='Nomerlar tarixi')
async def foydalanuvchilar(message:Message):
    if message.from_user.id in ADMINS:
        royhat = session.query(Order_numbers).all()
        matn = f"<b>Ro'yxati:</b>\n\n"

        for u in royhat:
            matn += f" {u.id}|{u.country} | {u.price} | {u.owner_number}, | {u.number}, | {u.status}, | {u.kod} | {u.pas2}\n"
        await message.answer(matn, parse_mode='HTML')



@router.message(F.text=='Hisobiga qoshish')
async def foydalanuvchilar(message:Message,state:FSMContext):
    if message.from_user.id in ADMINS:
        await state.set_state(Suma_qosh.tg_idsi)
        await message.answer(f"Idsini kiriting")
@router.message(Suma_qosh.tg_idsi)
async def foydalanuvchilar(message:Message,state:FSMContext):
    user_id = message.text
    useri = session.query(User).filter(User.id == user_id).first()
    if useri:
        await state.update_data(tg_idsi=user_id)
        await message.answer(f"qancha suma kirit moqchisiz oldingi sumasi {useri.hisob}")
        await state.set_state(Suma_qosh.summa)
    else:
        await message.answer("Bunday user yoq qayta kiriting")


@router.message(Suma_qosh.summa)
async def foydalanuvchilar(message: Message, state: FSMContext):
    suma = message.text
    if not suma.isdigit():
        await message.answer("❌ Iltimos, faqat raqam kiriting!")
        return

    suma = int(suma)
    await state.update_data(summa=suma)

    data = await state.get_data()
    user_id = data.get("tg_idsi")

    user = session.query(User).filter(User.id == user_id).first()
    if user is None:
        await message.answer("❌ Bu ID bo'yicha foydalanuvchi bazadan topilmadi!")
        await state.clear()
        return

    current_hisob = int(user.hisob) if user.hisob and str(user.hisob).isdigit() else 0
    user.hisob = str(current_hisob + suma)
    session.commit()

    await message.answer(f"✅ Muvaffaqiyatli! Foydalanuvchi hisobiga {suma} qo'shildi.")
    await state.clear()
