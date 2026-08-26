from aiogram import Router,F

from aiogram.types import Message, CallbackQuery

from keyboards.inline.nomer import generate_countries_keyboard, number_ols
from keyboards.inline.support import support
from keyboards.inline.tolov import tolov_qilish,tolov_tur
from utils.db_api.create_user import *
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
router = Router()

@router.message((F.text=='Kabinet') | (F.text == '/balance'))
async def menu(message:Message):
    user = session.get(User, message.from_user.id)
    await message.answer(f"""<b><tg-emoji emoji-id='5442804194983554178'>📁</tg-emoji> Kabinet ID:</b> <code>{user.id} </code>

<b><tg-emoji emoji-id='5443008004066651784'>💳</tg-emoji> Hisobingiz:</b>{user.hisob}  so'm""",reply_markup=tolov_qilish,parse_mode='HTML')


@router.message((F.text=='Nomer olish') | (F.text=='/buy_number'))
async def menu(message:Message):
    await message.answer(f"""📶 <b>Tayyor Telegram akkauntlar</b> — bu oldindan ro‘yxatdan o‘tgan, ishlashga tayyor akkauntlar bo‘lib, sizga doimiy foydalanish uchun taqdim etiladi.

<b>📌 Ishlash tartibi:</b>
1️⃣ Bot sizga akkaunt raqamini beradi.  
2️⃣ Shu raqam orqali Telegramga kirasiz (<b>Rasmiy ko‘k Telegram ilovasidan FOYDALANMANG, norasmiy ilovalardan foydalaning</b>).  
3️⃣ Telegram kod so‘raganda “<b>📲SMS olish</b>” tugmasini bosing va kuting.  
4️⃣ 1 daqiqa ichida sizga kirish kodi va 2 bosqichli parol taqdim etiladi.  
5️⃣ Muammo bo‘lsa, menyudagi Support orqali yordamga murojaat qiling.


✅ Barcha ma’lumotlarni o‘qib chiqqan bo‘lsangiz, “Tushundim” tugmasini bosing.""",reply_markup=number_ols,parse_mode='HTML')

@router.callback_query(F.data == 'nomer_ol')
async def raqam_olish(call:CallbackQuery):
    countries = session.query(Numbers_list.id, Numbers_list.country, Numbers_list.price).all()
    keyboard = generate_countries_keyboard(countries)
    await call.message.edit_text(f"""🌐 Eng arzonidan boshlab davlatlar ro'yxati

""",reply_markup=keyboard,parse_mode='HTML')

@router.callback_query(F.data == 'tolov_otish')
async def tolov_turi(call:CallbackQuery):
    await call.message.answer("🗃️ Kerakli to’lov tizimini tanlang:",reply_markup=tolov_tur)


@router.callback_query(F.data.startswith("countries_page:"))
async def tolov_turi(call:CallbackQuery):
    page = int(call.data.split(":")[1])

    countries = session.query(Numbers_list.id, Numbers_list.country, Numbers_list.price).all()

    keyboard = generate_countries_keyboard(countries, page=page)
    await call.message.edit_text("🌍 Kerakli davlatni tanlang:",reply_markup=keyboard)

@router.message((F.text=='Pul kiritish') | (F.text=='/deposit'))
async def menu(message:Message):
    await message.answer("🗃️ Kerakli to’lov tizimini tanlang:",reply_markup=tolov_tur)




@router.message((F.text == 'Nomerlarim') | (F.text=='/my_numbers'))
async def menu(message: Message):
    nomerlar = session.query(Order_numbers).filter(Order_numbers.owner_number == message.from_user.id).all()

    if not nomerlar:
        await message.answer("❌ Sizda hozircha sotib olingan raqamlar yo'q.")
        return

    keyboard = InlineKeyboardBuilder()
    for u in nomerlar:
        btn_text = f"{u.country} | {u.number}"
        keyboard.add(InlineKeyboardButton(text=btn_text, callback_data=f"nomer_info_{u.id}"))

    keyboard.adjust(1)

    await message.answer("<b>📋 Sizning raqamlaringiz ro'yxati:</b>\nKerakli raqamni ustiga bosing:",
                         reply_markup=keyboard.as_markup(), parse_mode='HTML')


@router.callback_query(F.data.startswith("nomer_info_"))
async def nomer_detail(call: CallbackQuery):
    nomer_id = int(call.data.split("_")[2])
    nomer = session.query(Order_numbers).filter(Order_numbers.id == nomer_id).first()

    if not nomer:
        await call.answer("❌ Bu raqam bazadan topilmadi!", show_alert=True)
        return

    info_text = (
        f"📌 <b>Raqam haqida ma'lumot:</b>\n\n"
        f"🆔 <b>ID:</b> {nomer.id}\n"
        f"🌍 <b>Davlat:</b> {nomer.country}\n"
        f"📞 <b>Raqam:</b> {nomer.number}\n"
        f"📊 <b>Status:</b> {nomer.status}\n"
        f"🔑 <b>Kod:</b> {nomer.kod}\n"
        f"🔐 <b>Parol (pas2):</b> {nomer.pas2}"
    )

    await call.message.answer(info_text, parse_mode='HTML')
    await call.answer()


@router.callback_query(F.data.startswith("nomer_info_"))
async def nomer_detail(call: CallbackQuery):
    nomer_id = int(call.data.split("_")[2])
    nomer = session.query(Order_numbers).filter(Order_numbers.id == nomer_id).first()

    if not nomer:
        await call.answer("❌ Bu raqam bazadan topilmadi!", show_alert=True)
        return

    info_text = (
        f"📌 <b>Raqam haqida ma'lumot:</b>\n\n"
        f"🆔 <b>ID:</b> {nomer.id}\n"
        f"🌍 <b>Davlat:</b> {nomer.country}\n"
        f"📞 <b>Raqam:</b> {nomer.number}\n"
        f"📊 <b>Status:</b> {nomer.status}\n"
        f"🔑 <b>Kod:</b> {nomer.kod}\n"
        f"🔐 <b>Parol (pas2):</b> {nomer.pas2}"
    )

    await call.message.answer(info_text, parse_mode='HTML')
    await call.answer()


@router.message((F.text == 'Support') | (F.text=='/support'))
async def menu(message: Message):

    await message.answer("""<b>🆘 SUPPORT – Qo‘llab-quvvatlash xizmati</b>

Savollaringiz yoki muammolaringiz bormi? Biz sizga tez va samarali yordam beramiz!""",
                         reply_markup=support, parse_mode='HTML')


@router.message((F.text=='Qolanma') | (F.text=='/faq'))
async def qolanma(messege: Message):
    await messege.answer(f"""📖 <b>Botdan foydalanish bo'yicha qo'llanma

Hurmatli foydalanuvchi! Botimiz orqali virtual raqamlar sotib olish va ularga kelgan SMS kodlarni qabul qilish juda oson. Quyidagi bo'limlardan keraklisini tanlab tanishib chiqing:</b>

💳 <b>1. Hisobni to'ldirish:</b>
<blockquote expandable>• Asosiy menyudan <b>"Pul kitish"</b>  bo'limini tanlab, to'lov tizimi (Click, Payme va h.k.) orqali mablag' kiriting.
• Pul avtomatik ravishda balansingizga qo'shiladi.</blockquote>

📲 <b>2. Raqam olish va SMS kodni qabul qilish:</b>
<blockquote expandable><b>Tayyor Telegram akkauntlar</b> — bu oldindan ro‘yxatdan o‘tgan, ishlashga tayyor akkauntlar bo‘lib, sizga doimiy foydalanish uchun taqdim etiladi.

<b>📌 Ishlash tartibi:</b>
• Bot sizga akkaunt raqamini beradi.  
• Shu raqam orqali Telegramga kirasiz (<b>Rasmiy ko‘k Telegram ilovasidan FOYDALANMANG, norasmiy ilovalardan foydalaning</b>).  
• Telegram kod so‘raganda “<b>📲SMS olish</b>” tugmasini bosing va kuting.  
• 1 daqiqa ichida sizga kirish kodi va 2 bosqichli parol taqdim etiladi.  
• Muammo bo‘lsa, menyudagi Support orqali yordamga murojaat qiling.</blockquote>

⚠️ <i>Eslatma: Agar SMS biroz kechikib kelsa, "📲 SMS olish" tugmasini bir necha soniyadan so'ng qayta bosing.</i>""",parse_mode='HTML')