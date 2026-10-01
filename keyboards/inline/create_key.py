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
                InlineKeyboardButton(text='API DOCS',url='https://xbomer.uz/api/',icon_custom_emoji_id="5370604433233177619"),
            ],
            [
                InlineKeyboardButton(text='API kalitni yangilish', icon_custom_emoji_id='6012661228910939253',
                                     callback_data='updatekey')

            ]
        ]
    )
    return keyboard