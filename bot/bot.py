from aiogram import Bot, Dispatcher

class SupportBot:
    def __init__(self, token, api_url):
        self.bot = Bot(token)
        self.dp = Dispatcher()  
        self.api_url = api_url

    def register_handlers(self):
        from handlers import router
        self.dp.include_router(router)

    async def run(self):
        self.register_handlers()  
        await self.dp.start_polling(self.bot)