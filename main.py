from clients import bot, db
from pyrogram import idle


async def main():
    print("[INFO] Initializing database...")
    await db.init()
    print("[INFO] Database initialized.")
    print("[INFO] Starting bot...")
    await bot.start()
    print("[INFO] Bot started.")
    print(f"\n[INFO] ------\nID\t: {bot.me.id}\nName\t: {bot.me.first_name}\nUsername: {bot.me.username}\n")
    await idle()
    print("[INFO] Exiting...")
    await bot.stop()
    print("[INFO] All clients stopped.")

if __name__ == "__main__":
    bot.run(main())