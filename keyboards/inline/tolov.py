from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup

tolov_qilish = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Pul kiritish",callback_data="tolov_otish",icon_custom_emoji_id="5976377521287990495")]
])

tolov_tur = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Click [avto]',callback_data='tolov_qilish',icon_custom_emoji_id='5305525714374645893'),
    ],
    [
        InlineKeyboardButton(text='Admin orqali',url='https://t.me/itredr',icon_custom_emoji_id='5190498849440931467')
    ]
])

