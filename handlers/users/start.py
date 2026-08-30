from aiogram import Router,F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.default.menu import menu
from utils.db_api.create_user import session, User

router = Router()


@router.message(CommandStart())
async def bot_start(message: Message):
    username = None
    user = session.query(User).filter(User.id == message.from_user.id).first()
    if user:
        await message.answer(f"""<b>👋 Assalomu alaykum X BOMER | foydalanuvchisi !</b>

<b>🚀 Ushbu bot sizga Telegram tarmoqlari uchun ishonchli va kafolatliy  TG profil xizmatlarini taklif etadi!
💫Bizning botimizga obuna bo'ling va do'stlaringiz bilan baham ko'ring
👇Davom etish uchun quyidagi tugmalardan birini tanlang</b>

<b>👤ID raqam:</b> <code>{message.from_user.id}</code>""""", reply_markup=menu, parse_mode='HTML')

    else:
        if message.from_user.username:
            username = message.from_user.username
        new_user = User(id=message.from_user.id,username=username, name=message.from_user.full_name)
        session.add(new_user)
        session.commit()
        session.close()
        await message.answer(f"""<b>👋 Assalomu alaykum X BOMER | foydalanuvchisi !

🤖 Bizning nakrutka botimizga xush kelibsiz: 👇
Ijtimoiy tarmoqlar</b> <i>( Telegram, Instagram, Tiktok va Youtube ) uchun obunachi, like, ko'rishlar hamda reaksiyalarni ko'paytirishingiz mumkin</i>

<b>👤ID raqam:</b> <code>{message.from_user.id}</code>""""", reply_markup=menu, parse_mode='HTML')




