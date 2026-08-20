from aiogram.types import InlineKeyboardButton,InlineKeyboardMarkup

tolov_qilish = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Tolov qilish📲",callback_data="tolov_qilish")]
])


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_payment_keyboard(pay_url: str, order_id: str, telegram_id: str, summasi: str):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                # To'lov qilish havolasi (Inpay'dan kelgan pay_url)
                InlineKeyboardButton(text="💳 To'lov qilish", url=pay_url),
            ],
            [
                # O'zgaruvchini callback_data ichiga f-string yordamida beramiz
                InlineKeyboardButton(text="🔄 To'lovni tekshirish", callback_data=f"check_pay:{order_id}:{telegram_id}:{summasi}")
            ]
        ]
    )
    return keyboard