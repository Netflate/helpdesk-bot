import asyncio
from dotenv import load_dotenv
import os 
from bot import SupportBot  
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")


async def main():
    bot = SupportBot(token=BOT_TOKEN, api_url=API_URL)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
