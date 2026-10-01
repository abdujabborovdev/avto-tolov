
from aiogram import Router, F

from aiogram.types import Message, CallbackQuery

from sqlalchemy import select
from keyboards.inline.nomer import generate_countries_keyboard, number_ols
from keyboards.inline.support import support, devo
from keyboards.inline.create_key import create_key, secret_key_inb
from keyboards.inline.tolov import tolov_qilish, tolov_tur
from utils.db_api.create_user import *  # async_session, User, Numbers_list, Order_numbers, SecretApiKey va h.k.
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message((F.text == 'Kabinet') | (F.text == '/balance'))
async def menu(message: Message):
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)

    await message.answer(f"""<b><tg-emoji emoji-id='5442804194983554178'>📁</tg-emoji> Kabinet ID:</b> <code>{user.id} </code>

<b><tg-emoji emoji-id='5443008004066651784'>💳</tg-emoji> Hisobingiz:</b>{user.hisob}  so'm""", reply_markup=tolov_qilish, parse_mode='HTML')


@router.message((F.text == 'Nomer olish') | (F.text == '/buy_number'))
async def menu(message: Message):
    await message.answer(f"""<tg-emoji emoji-id='5104966345267610825'>📶</tg-emoji> <b>Tayyor Telegram akkauntlar</b> — bu oldindan ro‘yxatdan o‘tgan, ishlashga tayyor akkauntlar bo‘lib, sizga doimiy foydalanish uchun taqdim etiladi.

<b><tg-emoji emoji-id='5462912132351797094'>📌</tg-emoji> Ishlash tartibi:</b>
<blockquote expandable><tg-emoji emoji-id='5382322671679708881'>✅</tg-emoji> Bot sizga akkaunt raqamini beradi.  
<tg-emoji emoji-id='5381990043642502553'>✅</tg-emoji> Shu raqam orqali Telegramga kirasiz (<b>Rasmiy ko‘k Telegram ilovasidan FOYDALANMANG, norasmiy ilovalardan foydalaning</b>).  
<tg-emoji emoji-id='5381879959335738545'>✅</tg-emoji> Telegram kod so‘raganda “<b>📲SMS olish</b>” tugmasini bosing va kuting.  
<tg-emoji emoji-id='5382054253403577563'>✅</tg-emoji> Sizga kirish kodi va 2 bosqichli parol taqdim etiladi.  
<tg-emoji emoji-id='5391197405553107640'>✅</tg-emoji> Muammo bo‘lsa, menyudagi Support orqali yordamga murojaat qiling.<blockquote>


<tg-emoji emoji-id='5427009714745517609'>✅</tg-emoji> Barcha ma’lumotlarni o‘qib chiqqan bo‘lsangiz, “Tushundim” tugmasini bosing.""", reply_markup=number_ols, parse_mode='HTML')


@router.callback_query(F.data == 'nomer_ol')
async def raqam_olish(call: CallbackQuery):
    async with async_session() as session:
        result = await session.execute(
            select(Numbers_list.id, Numbers_list.country, Numbers_list.price)
        )
        countries = result.all()

    keyboard = generate_countries_keyboard(countries)
    await call.message.edit_text(f"""<tg-emoji emoji-id='5188381825701021648'>🌐</tg-emoji> Eng arzonidan boshlab davlatlar ro'yxati

""", reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(F.data == 'tolov_otish')
async def tolov_turi(call: CallbackQuery):
        await call.message.answer("<tg-emoji emoji-id='5314787416211481862'>🗃️</tg-emoji> Kerakli to’lov tizimini tanlang:", reply_markup=tolov_tur)


@router.callback_query(F.data.startswith("countries_page:"))
async def tolov_turi(call: CallbackQuery):
    page = int(call.data.split(":")[1])

    async with async_session() as session:
        result = await session.execute(
            select(Numbers_list.id, Numbers_list.country, Numbers_list.price)
        )
        countries = result.all()

    keyboard = generate_countries_keyboard(countries, page=page)
    await call.message.edit_text("<tg-emoji emoji-id='5188381825701021648'>🌐</tg-emoji> Kerakli davlatni tanlang:", reply_markup=keyboard)


@router.message((F.text == 'Pul kiritish') | (F.text == '/deposit'))
async def menu(message: Message):
    await message.answer("<tg-emoji emoji-id='5314787416211481862'>🗃️</tg-emoji> Kerakli to’lov tizimini tanlang:", reply_markup=tolov_tur)


@router.message((F.text == 'Nomerlarim') | (F.text == '/my_numbers'))
async def menu(message: Message):
    async with async_session() as session:
        result = await session.execute(
            select(Order_numbers).filter(Order_numbers.owner_number == message.from_user.id)
        )
        nomerlar = result.scalars().all()

    if not nomerlar:
        await message.answer("<tg-emoji emoji-id='5465665476971471368'>❌</tg-emoji> Sizda hozircha sotib olingan raqamlar yo'q.")
        return

    keyboard = InlineKeyboardBuilder()
    for u in nomerlar:
        btn_text = f"{u.country} | {u.number}"
        keyboard.add(InlineKeyboardButton(text=btn_text, callback_data=f"nomer_info_{u.id}"))

    keyboard.adjust(1)

    await message.answer("<b><tg-emoji emoji-id='5197269100878907942'>📋</tg-emoji> Sizning raqamlaringiz ro'yxati:</b>\nKerakli raqamni ustiga bosing:",
                         reply_markup=keyboard.as_markup(), parse_mode='HTML')


@router.callback_query(F.data.startswith("nomer_info_"))
async def nomer_detail(call: CallbackQuery):
    nomer_id = int(call.data.split("_")[2])

    async with async_session() as session:
        result = await session.execute(select(Order_numbers).filter(Order_numbers.id == nomer_id))
        nomer = result.scalar_one_or_none()

    if not nomer:
        await call.answer("<tg-emoji emoji-id='5465665476971471368'>❌</tg-emoji> Bu raqam bazadan topilmadi!", show_alert=True)
        return

    info_text = (
        f"<tg-emoji emoji-id='5370604433233177619'>📌</tg-emoji> <b>Raqam haqida ma'lumot:</b>\n\n"
        f"<tg-emoji emoji-id='5974526806995242353'>🆔</tg-emoji> <b>ID:</b> {nomer.id}\n"
        f"<tg-emoji emoji-id='5397575638146110953'>🌍</tg-emoji> <b>Davlat:</b> {nomer.country}\n"
        f"<tg-emoji emoji-id='5467539229468793355'>📞</tg-emoji> <b>Raqam:</b> {nomer.number}\n"
        f"<tg-emoji emoji-id='5350398227013188928'>📊</tg-emoji> <b>Status:</b> {nomer.status}\n"
        f"<tg-emoji emoji-id='5330115548900501467'>🔑</tg-emoji> <b>Kod:</b> {nomer.kod}\n"
        f"<tg-emoji emoji-id='5472308992514464048'>🔐</tg-emoji> <b>Parol (pas2):</b> {nomer.pas2}"
    )

    await call.message.answer(info_text, parse_mode='HTML')
    await call.answer()



@router.message((F.text == 'Qo‘llab quvvatlash') | (F.text == '/support'))
async def menu(message: Message):

    await message.answer("""<tg-emoji emoji-id='5444965061749644170'>👨‍💻</tg-emoji> <b>Savol va Takliflar bo'lsa pastdagi manzilimizga murojaat qilishingiz mumkin!</b>""",
                         reply_markup=support, parse_mode='HTML')


@router.message((F.text == 'Qolanma') | (F.text == '/faq'))
async def qolanma(messege: Message):
    await messege.answer(f"""<tg-emoji emoji-id='5226512880362332956'>📖</tg-emoji> <b>Botdan foydalanish bo'yicha qo'llanma

Hurmatli foydalanuvchi! Botimiz orqali virtual raqamlar sotib olish va ularga kelgan SMS kodlarni qabul qilish juda oson. Quyidagi bo'limlardan keraklisini tanlab tanishib chiqing:</b>

<tg-emoji emoji-id='5305525714374645893'>💳</tg-emoji> <b>1. Hisobni to'ldirish:</b>
<blockquote expandable>• Asosiy menyudan <b>"Pul kitish"</b>  bo'limini tanlab, to'lov tizimi (Click, Payme va h.k.) orqali mablag' kiriting.
- Pul avtomatik ravishda balansingizga qo'shiladi.</blockquote>

<tg-emoji emoji-id='5406809207947142040'>📲</tg-emoji> <b>2. Raqam olish va SMS kodni qabul qilish:</b>
<blockquote expandable><b>Tayyor Telegram akkauntlar</b> — bu oldindan ro‘yxatdan o‘tgan, ishlashga tayyor akkauntlar bo‘lib, sizga doimiy foydalanish uchun taqdim etiladi.

<b><tg-emoji emoji-id='5370604433233177619'>📌</tg-emoji> Ishlash tartibi:</b>
- Bot sizga akkaunt raqamini beradi.  
- Shu raqam orqali Telegramga kirasiz (<b>Rasmiy ko‘k Telegram ilovasidan FOYDALANMANG, norasmiy ilovalardan foydalaning</b>).  
- Telegram kod so‘raganda “<b><tg-emoji emoji-id='5406809207947142040'>📲</tg-emoji>SMS olish</b>” tugmasini bosing va kuting.  
- 1 daqiqa ichida sizga kirish kodi va 2 bosqichli parol taqdim etiladi.  
- Muammo bo‘lsa, menyudagi Support orqali yordamga murojaat qiling.</blockquote>

<tg-emoji emoji-id='5462935376714802451'>⚠️</tg-emoji> <i>Eslatma: Agar SMS biroz kechikib kelsa, "<tg-emoji emoji-id='5406809207947142040'>📲</tg-emoji> SMS olish" tugmasini bir necha soniyadan so'ng qayta bosing.</i>""", parse_mode='HTML')


@router.message((F.text == 'Hamkorlik') | (F.text == '/hamkorlik'))
async def hamkorlik(message: Message):
    async with async_session() as session:
        result = await session.execute(
            select(SecretApiKey).filter(SecretApiKey.user_telegram_id == message.from_user.id)
        )
        secret_key = result.scalar_one_or_none()

        result = await session.execute(select(User).filter(User.id == message.from_user.id))
        user = result.scalar_one_or_none()

    if secret_key:
        keyboard = secret_key_inb()
        await message.answer(f"""<b><tg-emoji emoji-id='5307544885874664176'>⚙️</tg-emoji> Api dokument:</b>
<tg-emoji emoji-id='5375129357373165375'>🔗</tg-emoji> https://xbomer.uz/api/

<b><tg-emoji emoji-id='5330115548900501467'>🔑</tg-emoji> Ilk Api xizmat:</b>
<tg-emoji emoji-id='5375129357373165375'>🔗</tg-emoji> https://xbomer.uz/api/v1

<b><tg-emoji emoji-id='5330115548900501467'>🔑</tg-emoji> Sizning API kalitingiz:</b> <code>{secret_key.secret_api_key}</code>

<b><tg-emoji emoji-id='5296565124104993719'>💵</tg-emoji> Balansingiz:</b> {user.hisob} so'm""", reply_markup=keyboard)
    else:
        owner_id = int(message.from_user.id)
        create_button = create_key(owner_id=owner_id)
        await message.answer(f"""<b>Hamkorlik dasturidan foydalanish uchun API kalit yaratishingiz kerak <tg-emoji emoji-id='5427009714745517609'>✅</tg-emoji></b>

<blockquote expandable>• API kalit yaratish uchun pasdagi <b><tg-emoji emoji-id='5330115548900501467'>🔑</tg-emoji> Kalit yaratish</b> tugmasini bosing 
- Kalitingizni boshqa odamga korsatmang va yubormang
- Va havsiz joyda saqlang</blockquote>""", reply_markup=create_button, parse_mode='HTML')



@router.message(F.text=='/dev')
async def raqam_olish(message:Message):

    await message.answer(f"""<b><tg-emoji emoji-id='5444965061749644170'>👨‍💻</tg-emoji> Bot dasturchisi: @biloliddinabdujabborov

<blockquote expandable><tg-emoji emoji-id='5409048419211682843'>💵</tg-emoji> Siz ham o'z telegram botingizni yaratib daromad qilishni boshlang! Botlarga rasmiy ravishda avtomatik to'lov tizimlari qo'shilgan.</blockquote>

<tg-emoji emoji-id='5406745015365943482'>⬇️</tg-emoji> Sizga ham shunday turdagi bot kerak boʻlsa bizga murojaat qilishingiz mumkin!</b>""", reply_markup=devo, parse_mode='HTML')


