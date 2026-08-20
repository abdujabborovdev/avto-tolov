from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.inline.tolov import tolov_qilish
from utils.db_api.create_user import *
from states.tolov_qilish import *
from keyboards.inline import *
router = Router()


@router.message(CommandStart())
async def bot_start(message: Message, state: FSMContext):
    username = None
    user = session.get(User, message.from_user.id)
    if user:
        hisob = user.hisob
        await message.answer(f"Salom, {message.from_user.full_name}!{hisob}",reply_markup=tolov_qilish)
    else:
        if message.from_user.username:
            username = message.from_user.username
        new_user = User(id=message.from_user.id,username=username, name=message.from_user.full_name)
        session.add(new_user)
        session.commit()
        session.close()
        await message.answer(f"Salom, {message.from_user.full_name}!, Royhatdan otingiz",reply_markup=tolov_qilish)


