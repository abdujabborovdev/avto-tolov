from aiogram import Router, F
from keyboards.inline.nomer import *
from aiogram.types import Message, CallbackQuery
from data.config import *
import aiohttp
from data.config import ADMINS
from utils.db_api.create_user import session, User, Transaction, Numbers_list, Order_numbers

router = Router()
URL = 'https://seensms.uz/api/v1'

SEENSMS_KEY = SEENSMS_KEY

active_number_purchases = set()


@router.callback_query(F.data.startswith("country:"))
async def nomer_detail_handler(call: CallbackQuery):
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
async def buy_number_handler(call: CallbackQuery):
    user_id = call.from_user.id

    if user_id in active_number_purchases:
        await call.answer("⏳ So'rovingiz bajarilmoqda, biroz kuting...", show_alert=False)
        return

    active_number_purchases.add(user_id)

    try:
        data_name = call.data.split(':')
        country_name = data_name[1]
        price = int(data_name[2])
        tg_id = int(data_name[3])

        user = session.query(User).filter(User.id == tg_id).first()
        if not user:
            await call.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
            return

        try:
            hisobi = int(user.hisob) if user.hisob is not None else 0
        except (ValueError, TypeError):
            hisobi = 0

        if hisobi < price:
            await call.answer("❌ Mablag'ingiz yetarli emas!", show_alert=True)
            return

        await call.message.edit_text("⏳ Raqam qidirilmoqda, iltimos kuting...")

        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.post(URL, data={
                    'key': f'{SEENSMS_KEY}',
                    'action': 'accounts_get',
                    'country': f'{country_name}'
                }) as r:
                    dat = await r.json()
        except Exception as e:
            await call.message.edit_text(f"❌ Xatolik yuz berdi: {e}\nQayta urinib ko'ring.")
            return

        if isinstance(dat, dict) and dat.get('number'):
            session.refresh(user)
            current_hisob = int(user.hisob) if user.hisob is not None else 0

            if current_hisob < price:
                await call.message.edit_text("❌ Xatolik: Mablag'ingiz yetarli emas!")
                return

            user.hisob = current_hisob - price

            num_id = int(dat.get('id'))
            num_country = dat.get('country')
            number = dat.get('number')

            new_number_order = Order_numbers(
                id=num_id,
                country=num_country,
                owner_number=tg_id,
                number=number
            )
            session.add(new_number_order)
            session.commit()

            masked_num = (
                    number[:3] + '*' * (len(str(number)) - 5) + str(number)[-2:]
            )

            CHANNEL_ID = '-1004365925735'
            try:
                await call.bot.send_message(
                    CHANNEL_ID,
                    text=(
                        f'🔔 <b>Yangi raqam sotib olindi!</b>\n\n'
                        f'🌍 Davlat: {num_country}\n'
                        f'📞 Nomer: <code>{masked_num}</code>'
                    ),
                    parse_mode='HTML',
                )
            except Exception as e:
                print(f'Kanalga yuborishda xatolik: {e}')

            keyboard = check_number(num_id)
            for admin_id in ADMINS:
                try:
                    await call.bot.send_message(
                        admin_id,
                        f"🔔 <b>Yangi raqam sotib olindi!</b>\n\n"
                        f"👤 Xaridor ID: <code>{tg_id}</code>\n"
                        f"🌍 Davlat: {num_country}\n"
                        f"📞 Nomer: <code>{number}</code>\n"
                        f"🆔 ID: {num_id}",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

            await call.message.edit_text(
                f"""✅ Muvaffaqiyatli raqam olindi!\n\n<b>Nomer:</b> {number} \n<b>id:</b> {num_id}""",
                parse_mode='HTML',
                reply_markup=keyboard
            )
        else:
            error_msg = dat.get('message', "Hozirda bu davlatda bo'sh raqamlar yo'q!") if isinstance(dat,
                                                                                                     dict) else "Noma'lum xatolik"
            await call.message.edit_text(f"❌ Raqam berilmadi.\nSabab: {error_msg}")
    finally:
        active_number_purchases.discard(user_id)


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