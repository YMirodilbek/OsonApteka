import asyncio
from aiogram import Bot, Dispatcher
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


TOKEN = "7886547250:AAFv0cFJc607ZTRsLHgl_ldRcDGyg5CS9l0"
router = Router()
dp = Dispatcher()

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:

    await message.answer(f"{message.from_user.id}")
    
async def main() -> None:
    bot = Bot(token=TOKEN)
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
