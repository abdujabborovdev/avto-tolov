from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu = ReplyKeyboardMarkup(keyboard=
        [

        [
            KeyboardButton(text='Nomer olish',icon_custom_emoji_id='5467539229468793355'),
            KeyboardButton(text='Nomerlarim',icon_custom_emoji_id='5431499171045581032')
        ],
            [
            KeyboardButton(text='Pul kiritish',icon_custom_emoji_id='5296565124104993719'),
            KeyboardButton(text='Kabinet',icon_custom_emoji_id='5359785904535774578')
            ],
[
            KeyboardButton(text='Qolanma',icon_custom_emoji_id='5373098009640836781'),
            KeyboardButton(text='Support',icon_custom_emoji_id='5220108512893344933')
        ],
            [
              KeyboardButton(text="Hamkorlik",icon_custom_emoji_id='5357080225463149588')
            ],

        ],resize_keyboard=True
)