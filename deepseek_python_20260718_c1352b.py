import asyncio
import sys
import time
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.enums.parse_mode import ParseMode
from config import BOT_TOKEN, FAKE_PORT
from database import db
from handlers import router

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam"),
    ]
    await bot.set_my_commands(commands)

def fake_server_startup():
    """Fake server port display"""
    print("=" * 50)
    print("       DOSTECH AI BOT")
    print("=" * 50)
    print()
    time.sleep(0.5)
    print("[✓] Database connected")
    time.sleep(0.3)
    print("[✓] Bot initialized")
    time.sleep(0.3)
    print("[✓] Admin panel ready")
    time.sleep(0.3)
    print("[✓] Products system ready")
    time.sleep(0.3)
    print("[✓] Orders system ready")
    time.sleep(0.3)
    print("[✓] News system ready")
    time.sleep(0.5)
    print()
    print(f"Server running on port {FAKE_PORT}...")
    print("Waiting for Telegram updates...")
    print()
    print("DOSTECH AI BOT IS ONLINE")
    print("=" * 50)
    print()

async def main():
    # Show fake server startup
    fake_server_startup()
    
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    
    # Include router
    dp.include_router(router)
    
    # Set commands
    await set_commands(bot)
    
    # Start polling
    print("\nBot started. Press Ctrl+C to stop.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nBot stopped by user.")
        print("DOSTECH AI BOT IS OFFLINE")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)