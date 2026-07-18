import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Bot settings
BOT_NAME = "DOSTECH AI"
COMPANY_NAME = "DOSTECH AI"

# Links
TELEGRAM_CHANNEL = "https://t.me/dostech_ai"
TELEGRAM_CONTACT = "https://t.me/dostech_support"
INSTAGRAM = "https://instagram.com/dostech_ai"
WEBSITE = "https://dostech.ai"

# Database
DATABASE_NAME = "dostech_bot.db"

# Fake server settings
FAKE_PORT = 8080
