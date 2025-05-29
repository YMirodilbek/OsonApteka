
from aiogram.filters import CommandStart ,CommandObject
from aiogram import Bot, Dispatcher, types
from asgiref.sync import sync_to_async
from pathlib import Path
import asyncio
import django
import sys
import os



BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Admin.settings')
django.setup()

from main.models import CustomUser

TOKEN = '7886547250:AAFv0cFJc607ZTRsLHgl_ldRcDGyg5CS9l0'  # Tokeningizni shu yerga yozing

bot = Bot(token=TOKEN)
dp = Dispatcher()
from urllib.parse import unquote

@dp.message(CommandStart(deep_link=True))
async def start_handler(message: types.Message, command: CommandObject):
    raw_token = command.args
    if not raw_token:
        await message.answer("❗ Token topilmadi.")
        return

    token = unquote(raw_token).strip()  # URL dan yechib olib, bo‘sh joylarni tozalaymiz

    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_token=token)
        user.telegram_id = message.from_user.id
        await sync_to_async(user.save)()
        await message.answer(f"✅ Telegram profilingizga ulandi! ID: {user.telegram_id}")
    except CustomUser.DoesNotExist:
        await message.answer(f"❌ Token noto‘g‘ri: {token}")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())