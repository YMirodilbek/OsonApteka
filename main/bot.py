
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
@dp.message(CommandStart(deep_link=True))
async def start_handler(message: types.Message, command: CommandObject):
    token = command.args
    if not token:
        await message.answer("❗ Token topilmadi.")
        return

    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_token=token)
        user.telegram_id = message.from_user.id
        await sync_to_async(user.save)()

        await message.answer(f"✅ Telegram profilingizga ulandi!{user.telegram_id}")
    except CustomUser.DoesNotExist:
        await message.answer("❌ Token noto‘g‘ri.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())