from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

import keyboards

admin_k = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='Foydalanuvchilar'),
        KeyboardButton(text='Tolovlar tarixi')
    ],
    [
        KeyboardButton(text='Nomerlar royhati'),
        KeyboardButton(text='Nomerlarni yangilash')
    ],
    [
        KeyboardButton(text='Hisobiga qoshish'),
        KeyboardButton(text='Nomerlar tarixi'),

    ],
    [
        KeyboardButton(text='Habar yuborish')
    ]

],resize_keyboard=True)