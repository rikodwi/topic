import config, sys

from pyrogram import Client as RawClient, errors, types

commands_owner = [
    types.BotCommand(command="mygroups", description="My Groups"),
    types.BotCommand(command="addtopic", description="Add Topic"),
    types.BotCommand(command="deltopic", description="Hapus Topic"),
    types.BotCommand(command="addtour", description="Acc Chat"),
]

class Client(RawClient):
    def __init__(self):
        super().__init__(
            "Topic-Bot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins=dict(root="plugins"),
            workers=8,
            max_concurrent_transmissions=4,
        )

    async def start(self):
        await super().start()
        print(bot.me.username)
        # if not config.CHANNEL_LOG:
        #     print('[PERINGATAN] Sepertinya channel log belum diisi.')
        #     sys.exit()
        #     return
        # print("[INFO] Mengambil data Channel LOG")
        # try:
        #     data = await self.get_chat(config.CHANNEL_LOG)
        #     print(f"[INFO] Berhasil menggambil data\n[INFO] Title: {data.title}")
        #     print(f"[INFO] Link: {data.invite_link}\n")
        # except:
        #     print("[PERINGATAN] Pastikan bot telah menjadi admin.")
            # sys.exit()
            # return
        print("[INFO] registering commands...")
        await self._register_commands()
        print("[INFO] commands registered.")


    async def _register_commands(self):
        try:
            await self.set_bot_commands(commands_owner, scope=types.BotCommandScopeAllPrivateChats())
            print("[INFO] Berhasil mendaftarkan commands")
        except:
            print("[INFO] Gagal mendaftarkan commands")
        pass
            
bot = Client()