from idlelib import rpc

from aiogram import Router, F
from keyboards.inline.nomer import *
from aiogram.types import Message, CallbackQuery
from data.config import *
import aiohttp

from keyboards.inline.tolov import tolov_qilish
from utils.db_api.create_user import session, User, Transaction, Numbers_list, Order_numbers

router = Router()
URL = 'https://seensms.uz/api/v1'

SEENSMS_KEY = SEENSMS_KEY


@router.callback_query(
    F.data.startswith("country:"))
async def nomer(call: CallbackQuery, ):
    data_name = call.data.split(':')
    country_name = data_name[1]
    Number = session.query(Numbers_list).filter(Numbers_list.country == country_name).first()
    if Number:
        tgid = call.from_user.id
        keyboar = buy_number(country=Number.country, price=Number.price, tg_id=tgid)
        await call.message.edit_text(f"""<b>Davlat:</b> {Number.country}
<b>Narxi:</b> {Number.price}

<b> Tasdiqlash ✅</b> tugmasini bosing !""", parse_mode='HTML', reply_markup=keyboar)


@router.callback_query(F.data.startswith("buy_number:"))
async def nomer(call: CallbackQuery):
    data_name = call.data.split(':')
    country_name = data_name[1]
    price = int(data_name[2])
    tg_id = int(data_name[3])
    user = session.query(User).filter(User.id == tg_id).first()
    hisobi = int(user.hisob) if user and user.hisob and str(
        user.hisob).isdigit() else 0
    if hisobi >= price:
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.post(URL, data={
                    'key': f'{SEENSMS_KEY}',
                    'action': 'accounts_get',
                    'country': f'{country_name}'

                }) as r:
                    dat = await r.json()
        except Exception as e:
            await call.message.edit_text(f"""Xatolik {e}, Qayta urinib koring""")
            return  

        if isinstance(dat, dict) and dat.get(
                'number'):
            user.hisob = str(int(user.hisob) - int(
                price))
            session.commit()

            keyboard = check_number(dat.get('id'))

            num_id = int(dat.get('id'))
            num_country = dat.get('country')
            tg_id_owner = int(call.from_user.id)
            number = dat.get('number')
            new_number_order = Order_numbers(id=num_id, country=num_country, owner_number=tg_id_owner, number=number)
            session.add(new_number_order)
            session.commit()

            await call.message.edit_text(f"""✅Muvafiyaqiyatlik nomer olindi

<b>Nomer:</b> {number} 
<b>id:</b> {num_id}""", parse_mode='HTML', reply_markup=keyboard)
        else:
            error_msg = dat.get('message', "Hozirda bu davlatda bo'sh raqamlar yo'q!") if isinstance(dat,
                                                                                                     dict) else "Noma'lum xatolik"
            await call.message.edit_text(
                f"❌ Raqam berilmadi.\nSabab: {error_msg}")
    else:
        await call.message.edit_text("""Mablag'ingiz yetarlik emas❌,
Hisobingzni toldirng 💳""", reply_markup=tolov_qilish)


@router.callback_query(F.data.startswith('check_number:'))
async def check_num(call: CallbackQuery):
    data_id = call.data.split(':')
    number_id = int(data_id[1])
    number_order = session.query(Order_numbers).filter(
        Order_numbers.id == number_id).first()
    if not number_order:
        await call.answer("❌ Buyurtma topilmadi!", show_alert=True)
        return

    async with aiohttp.ClientSession() as r:
        async with r.post(URL, data={
            'key': f'{SEENSMS_KEY}',
            'action': 'accounts_code',
            'id': number_id
        }) as r:
            dat = await r.json()

    if isinstance(dat, dict) and dat.get('status'):
        if dat.get('status') == 'OK':
            kodi = int(dat.get('code'))
            pas2 = dat.get('password')
            number_order.status = 'OK'
            number_order.kod = kodi
            number_order.pas2 = dat.get('password')
            session.commit()
            await call.message.edit_text(f"""<b>✅ SMS muvafiyaqiyatlik olindi

Kod:</b> <code>{dat.get('code')}</code>
<b>Pass:</b> <code>{dat.get('password')}</code>

<i>Pass ni 2 boshqichlik parol soraganda kiritasiz</i>
""", parse_mode="HTML")
        elif dat.get('status') == 'WAITING':
            await call.answer('❌ Xali sms habar kelgani yoq birozdan song urinib koring', show_alert=True)