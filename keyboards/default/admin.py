from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

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

    ]

],resize_keyboard=True)