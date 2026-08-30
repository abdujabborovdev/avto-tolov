from aiogram import Router,F

from aiogram.types import  CallbackQuery
from utils.db_api.create_user import *
import secrets
from aiogram.exceptions import TelegramBadRequest
from keyboards.inline.create_key import secret_key_inb

router = Router()

@router.callback_query(F.data.startswith("createkey"))
async def create_key(call: CallbackQuery):
    await call.answer()
    data_id = call.data.split(":")[1]
    secret_key = secrets.token_hex(16)
    user_tg_id = int(data_id)
    user = session.query(User).filter(User.id == call.from_user.id).first()
    secret_keys = session.query(SecretApiKey).filter(SecretApiKey.user_telegram_id == call.from_user.id).first()
    user_hisob = user.hisob if user else 0
    if not secret_keys:
        new_key = SecretApiKey(user_telegram_id=user_tg_id, secret_api_key=secret_key)
        session.add(new_key)
        session.commit()
        session.close()
        keyboard = secret_key_inb()
        await call.message.edit_text(f"""<b>Muvafiyaqiyatlik kalit yaratildi <tg-emoji emoji-id='5370870691140737817'>🥳</tg-emoji>
        
⚙️ Api dokument:
🔗 https://xbomer.uz/api/
    
🔑 Ilk Api xizmat:
🔗 https://xbomer.uz/api/v1
    
🔑 Sizning API kalitingiz: <code>{secret_key}</code>
💵 Balansingiz:  {user_hisob} so'm </b>""",parse_mode="html",reply_markup=keyboard)
    else:
        try:
            await call.message.edit_text(
                f"Siz allaqachon kalit olgansiz <tg-emoji emoji-id='5427009714745517609'>✅</tg-emoji>",
                reply_markup=None,
                parse_mode="HTML"
            )
        except TelegramBadRequest:
            pass