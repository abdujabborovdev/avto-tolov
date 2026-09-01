# handlers/admin/api_keys.py

from contextlib import asynccontextmanager
from math import ceil

from aiogram import Router, F
from aiogram.filters import Filter
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, func, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

# ⚠️ O'z loyihangizdagi haqiqiy import yo'llariga moslang
from utils.db_api.create_user import SecretApiKey
from utils.db_api.create_user import async_session  # sessionmaker (async_sessionmaker)

router = Router()

PAGE_SIZE = 10
ADMIN_IDS = [123456789]  # <-- o'zingizning admin ID'laringizni kiriting


# ==========================================================
# ADMIN FILTER
# ==========================================================
class IsAdmin(Filter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return event.from_user.id in ADMIN_IDS



@asynccontextmanager
async def get_session(data: dict):

    session: AsyncSession | None = data.get("session")
    if session is not None:
        yield session
    else:
        async with async_session() as new_session:
            yield new_session


# ==========================================================
# CALLBACK DATA FACTORY'LARI
# ==========================================================
class ApiKeyListCB(CallbackData, prefix="apk_list"):
    page: int


class ApiKeyDetailCB(CallbackData, prefix="apk_detail"):
    id: int
    page: int


class ApiKeyDeleteCB(CallbackData, prefix="apk_del"):
    id: int
    page: int


class ApiKeyToggleCB(CallbackData, prefix="apk_toggle"):
    id: int
    page: int


# ==========================================================
# YORDAMCHI FUNKSIYALAR
# ==========================================================
async def get_total_pages(session: AsyncSession) -> int:
    total = (await session.execute(select(func.count()).select_from(SecretApiKey))).scalar_one()
    return max(1, ceil(total / PAGE_SIZE))


async def build_list_keyboard(session: AsyncSession, page: int):
    total_pages = await get_total_pages(session)
    page = max(0, min(page, total_pages - 1))

    stmt = (
        select(SecretApiKey)
        .order_by(SecretApiKey.id)
        .offset(page * PAGE_SIZE)
        .limit(PAGE_SIZE)
    )
    keys = (await session.execute(stmt)).scalars().all()

    builder = InlineKeyboardBuilder()
    for key in keys:
        status_emoji = "🔴" if key.is_blocked else "🟢"
        builder.button(
            text=f"{status_emoji} #{key.id} | {key.user_telegram_id}",
            callback_data=ApiKeyDetailCB(id=key.id, page=page).pack(),
        )
    builder.adjust(1)

    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data=ApiKeyListCB(page=page - 1).pack())
        )
    nav_row.append(
        InlineKeyboardButton(text=f"📄 {page + 1}/{total_pages}", callback_data="apk_noop")
    )
    if page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton(text="Oldinga ➡️", callback_data=ApiKeyListCB(page=page + 1).pack())
        )
    builder.row(*nav_row)

    return builder.as_markup(), keys, total_pages


def build_detail_text(key: SecretApiKey) -> str:
    status = "🔴 Bloklangan" if key.is_blocked else "🟢 Faol"
    return (
        f"🔑 <b>API Kalit ma'lumotlari</b>\n\n"
        f"🆔 <b>ID:</b> <code>{key.id}</code>\n"
        f"👤 <b>User ID:</b> <code>{key.user_telegram_id}</code>\n"
        f"🔐 <b>Secret Key:</b> <code>{key.secret_api_key}</code>\n"
        f"📊 <b>Holati:</b> {status}"
    )


def build_detail_keyboard(key: SecretApiKey, page: int):
    builder = InlineKeyboardBuilder()
    toggle_text = "🟢 Blokdan yechish" if key.is_blocked else "🔴 Bloklash"
    builder.button(text=toggle_text, callback_data=ApiKeyToggleCB(id=key.id, page=page).pack())
    builder.button(text="🗑 Kalitni o'chirish", callback_data=ApiKeyDeleteCB(id=key.id, page=page).pack())
    builder.button(text="⬅️ Ro'yxatga qaytish", callback_data=ApiKeyListCB(page=page).pack())
    builder.adjust(1)
    return builder.as_markup()


# ==========================================================
# 1) "Apilar" — ro'yxatni chiqarish
# ==========================================================
@router.message(IsAdmin(), F.text == "Apilar")
async def show_api_keys_list(message: Message, **data):
    async with get_session(data) as session:
        keyboard, keys, total_pages = await build_list_keyboard(session, page=0)

        if not keys:
            await message.answer("📭 Hozircha bazada API kalitlar mavjud emas.")
            return

        await message.answer(
            f"🔑 <b>API kalitlar ro'yxati</b> (Jami sahifalar: {total_pages})",
            reply_markup=keyboard,
        )


# ==========================================================
# 2) Sahifalash (Oldinga / Orqaga)
# ==========================================================
@router.callback_query(IsAdmin(), ApiKeyListCB.filter())
async def paginate_api_keys(call: CallbackQuery, callback_data: ApiKeyListCB, **data):
    async with get_session(data) as session:
        keyboard, keys, total_pages = await build_list_keyboard(session, page=callback_data.page)

        if not keys:
            await call.answer("📭 Bu sahifada kalitlar topilmadi.", show_alert=True)
            return

        await call.message.edit_text(
            f"🔑 <b>API kalitlar ro'yxati</b> (Jami sahifalar: {total_pages})",
            reply_markup=keyboard,
        )
        await call.answer()


@router.callback_query(F.data == "apk_noop")
async def noop_handler(call: CallbackQuery):
    await call.answer()


# ==========================================================
# 3) Bitta kalit haqida batafsil ma'lumot
# ==========================================================
@router.callback_query(IsAdmin(), ApiKeyDetailCB.filter())
async def show_api_key_detail(call: CallbackQuery, callback_data: ApiKeyDetailCB, **data):
    async with get_session(data) as session:
        key = await session.get(SecretApiKey, callback_data.id)

        if key is None:
            await call.answer("❌ Bu kalit topilmadi (o'chirilgan bo'lishi mumkin).", show_alert=True)
            return

        await call.message.edit_text(
            build_detail_text(key),
            reply_markup=build_detail_keyboard(key, callback_data.page),
        )
        await call.answer()


# ==========================================================
# 4) Kalitni o'chirish
# ==========================================================
@router.callback_query(IsAdmin(), ApiKeyDeleteCB.filter())
async def delete_api_key(call: CallbackQuery, callback_data: ApiKeyDeleteCB, **data):
    async with get_session(data) as session:
        key = await session.get(SecretApiKey, callback_data.id)

        if key is None:
            await call.answer("❌ Bu kalit allaqachon o'chirilgan.", show_alert=True)
            return

        await session.execute(sa_delete(SecretApiKey).where(SecretApiKey.id == callback_data.id))
        await session.commit()

        await call.answer("🗑 Kalit muvaffaqiyatli o'chirildi.", show_alert=True)

        # Ro'yxatga qaytarish
        keyboard, keys, total_pages = await build_list_keyboard(session, page=callback_data.page)

        if not keys and callback_data.page > 0:
            # Sahifa bo'sh qolsa, oldingi sahifaga qaytaramiz
            keyboard, keys, total_pages = await build_list_keyboard(session, page=callback_data.page - 1)

        if not keys:
            await call.message.edit_text("📭 Hozircha bazada API kalitlar mavjud emas.")
            return

        await call.message.edit_text(
            f"🔑 <b>API kalitlar ro'yxati</b> (Jami sahifalar: {total_pages})",
            reply_markup=keyboard,
        )



@router.callback_query(IsAdmin(), ApiKeyToggleCB.filter())
async def toggle_block_api_key(call: CallbackQuery, callback_data: ApiKeyToggleCB, **data):
    async with get_session(data) as session:
        key = await session.get(SecretApiKey, callback_data.id)

        if key is None:
            await call.answer("❌ Bu kalit topilmadi.", show_alert=True)
            return

        key.is_blocked = not key.is_blocked
        await session.commit()
        await session.refresh(key)

        status_text = "bloklandi 🔴" if key.is_blocked else "blokdan yechildi 🟢"
        await call.answer(f"✅ Kalit {status_text}.")

        await call.message.edit_text(
            build_detail_text(key),
            reply_markup=build_detail_keyboard(key, callback_data.page),
        )