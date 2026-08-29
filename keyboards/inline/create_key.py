from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup

def create_key(owner_id: int ):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Kalit yaratish ", callback_data=f"createkey:{owner_id}", icon_custom_emoji_id='5330115548900501467')
            ],
        ]
    )
    return keyboard

def secret_key_inb():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='📃 API DOCS',url='https://xbomer.uz/api/',),
            ],
            [
                InlineKeyboardButton(text='API kalitni yangilish', icon_custom_emoji_id='5264727218734524899',
                                     callback_data='updatekey')

            ]
        ]
    )
    return keyboard