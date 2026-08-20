from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Always load .env from the project folder, no matter where the bot is started from
load_dotenv(ENV_PATH, override=True)

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip().strip('"').strip("'")
ADMINS = [admin.strip() for admin in (os.getenv("ADMINS") or "").split(",") if admin.strip()]
IP = os.getenv("ip", "localhost")
INPAY_ID = os.getenv("INPAY_ID")
INPAY_TOKEN = os.getenv("INPAY_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylida topilmadi")
