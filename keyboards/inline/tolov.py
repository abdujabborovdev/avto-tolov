from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup

tolov_qilish = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💳 Pul kiritish",callback_data="tolov_otish")]
])

tolov_tur = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Payme.uz [avto]',callback_data='tolov_qilish',icon_custom_emoji_id='5287364801645796685'),

    ],
    [
        InlineKeyboardButton(text='Click.uz [avto]',callback_data='tolov_qilish',icon_custom_emoji_id='5348031828882111307')
     ],
    [
        InlineKeyboardButton(text='Admin orqali',url='https://t.me/itredr',icon_custom_emoji_id='5190498849440931467')
    ]
])

def get_payment_keyboard(pay_url: str, order_id: str, telegram_id: str, summasi: str):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 To'lov qilish", url=pay_url),
            ],
            [
                InlineKeyboardButton(text="✅ To'lov qildim", callback_data=f"check_pay:{order_id}:{telegram_id}:{summasi}")
            ]
        ]
    )
    return keyboard