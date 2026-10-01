
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from sqlalchemy import select
from keyboards.default.menu import menu
from utils.db_api.create_user import async_session, User

router = Router()


@router.message(CommandStart())
async def bot_start(message: Message):
    username = None

    async with async_session() as session:
        result = await session.execute(select(User).filter(User.id == message.from_user.id))
        user = result.scalar_one_or_none()

        if user:
            await message.answer(f"""<b><tg-emoji emoji-id='5472055112702629499'>👋</tg-emoji> Assalomu alaykum xbomer.uz | foydalanuvchisi !</b>

<blockquote expandable>/balance — <tg-emoji emoji-id='5976377521287990495'>💳</tg-emoji> Kabinetim
/buy_number — <tg-emoji emoji-id='6037418554276452311'>📱</tg-emoji> Hisob olish
/deposit — <tg-emoji emoji-id='5305525714374645893'>💰</tg-emoji> Pul kiritish
/my_numbers — <tg-emoji emoji-id='5197269100878907942'>📋</tg-emoji> Nomerlarim ro'yxati
/support — <tg-emoji emoji-id='5463289209005560690'>📞</tg-emoji> Qo'llab-quvvatlash
/faq — <tg-emoji emoji-id='5226512880362332956'>📖</tg-emoji> Qo'llanma
/dev — <tg-emoji emoji-id='5190458330719461749'>💻</tg-emoji> Dasturchi</blockquote>

<b><tg-emoji emoji-id='5256143829672672750'>👤</tg-emoji> ID raqam:</b> <code>{message.from_user.id}</code>""", reply_markup=menu, parse_mode='HTML')

        else:
            if message.from_user.username:
                username = message.from_user.username
            new_user = User(id=message.from_user.id, username=username, name=message.from_user.full_name)
            session.add(new_user)
            await session.commit()

            await message.answer(f"""<b><tg-emoji emoji-id='5472055112702629499'>👋</tg-emoji> Assalomu alaykum xbomer.uz | foydalanuvchisi !

<blockquote expandable>/balance — <tg-emoji emoji-id='5976377521287990495'>💳</tg-emoji> Kabinetim
/buy_number — <tg-emoji emoji-id='6037418554276452311'>📱</tg-emoji> Hisob olish
/deposit — <tg-emoji emoji-id='5305525714374645893'>💰</tg-emoji> Pul kiritish
/my_numbers — <tg-emoji emoji-id='5197269100878907942'>📋</tg-emoji> Nomerlarim ro'yxati
/support — <tg-emoji emoji-id='5463289209005560690'>📞</tg-emoji> Qo'llab-quvvatlash
/faq — <tg-emoji emoji-id='5226512880362332956'>📖</tg-emoji> Qo'llanma
/dev — <tg-emoji emoji-id='5190458330719461749'>💻</tg-emoji> Dasturchi</blockquote>

<b><tg-emoji emoji-id='5256143829672672750'>👤</tg-emoji> ID raqam:</b> <code>{message.from_user.id}</code>""", reply_markup=menu, parse_mode='HTML')