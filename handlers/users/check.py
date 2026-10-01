from datetime import datetime
from io import BytesIO
from zoneinfo import ZoneInfo

from aiogram.types import BufferedInputFile
from PIL import Image, ImageDraw, ImageFont

TZ = ZoneInfo("Asia/Tashkent")


def fmt(n) -> str:
    return f"{int(n):,}".replace(",", " ")


def chek_text(order_id, telegram_id, summa, balance, dt=None) -> str:
    dt = dt or datetime.now(TZ)
    return (
        "🧾 <b>TO'LOV CHEKI</b>\n"
        "━━━━━━━━━━━━━━━\n"
        f"📅 Sana: <b>{dt:%d.%m.%Y %H:%M}</b>\n"
        f"🆔 Buyurtma: <code>{order_id}</code>\n"
        f"👤 Foydalanuvchi ID: <code>{telegram_id}</code>\n"
        "💳 To'lov turi: <b>Click</b>\n"
        f"💵 Summa: <b>{fmt(summa)} so'm</b>\n"
        "✅ Holat: <b>To'langan</b>\n"
        "━━━━━━━━━━━━━━━\n"
        f"💰 Joriy balans: <b>{fmt(balance)} so'm</b>"
    )


def _font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def chek_image(order_id, telegram_id, summa, balance, dt=None) -> BufferedInputFile:
    """Rasmli chek (PNG) — Telegram'ga photo qilib yuboriladi."""
    dt = dt or datetime.now(TZ)
    W, H = 720, 1040
    img = Image.new("RGB", (W, H), "#eef1f6")
    d = ImageDraw.Draw(img)

    d.rounded_rectangle((40, 40, W - 40, H - 40), radius=36, fill="white")

    cx, cy, r = W // 2, 170, 64
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill="#22b45a")
    d.line([(cx - 28, cy + 2), (cx - 8, cy + 24), (cx + 30, cy - 22)],
           fill="white", width=13, joint="curve")

    d.text((W // 2, 290), "To'lov muvaffaqiyatli", font=_font(40), fill="#1c2733", anchor="mm")
    d.text((W // 2, 360), f"{fmt(summa)} so'm", font=_font(64), fill="#22b45a", anchor="mm")

    rows = [
        ("Sana", f"{dt:%d.%m.%Y %H:%M}"),
        ("Buyurtma", str(order_id)),
        ("Foydalanuvchi ID", str(telegram_id)),
        ("To'lov turi", "Click"),
        ("Holat", "To'langan"),
    ]
    y = 460
    for label, value in rows:
        d.text((90, y), label, font=_font(28), fill="#7a8794", anchor="lm")
        d.text((W - 90, y), value, font=_font(30), fill="#1c2733", anchor="rm")
        y += 78
        d.line((90, y - 39, W - 90, y - 39), fill="#e6e9ee", width=2)

    d.text((90, y + 30), "Joriy balans", font=_font(30), fill="#7a8794", anchor="lm")
    d.text((W - 90, y + 30), f"{fmt(balance)} so'm", font=_font(36), fill="#1c2733", anchor="rm")

    d.text((W // 2, H - 90), "Xaridingiz uchun rahmat!", font=_font(26), fill="#a0a9b4", anchor="mm")

    buf = BytesIO()
    img.save(buf, format="PNG")
    return BufferedInputFile(buf.getvalue(), filename=f"chek_{order_id}.png")


