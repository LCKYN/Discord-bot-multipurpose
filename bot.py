import os

from dotenv import load_dotenv
from interactions import Client, Extension, Intents, listen

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

bot = Client(intents=Intents.ALL | Intents.MESSAGE_CONTENT)


@listen()
async def on_ready():
    print("Ready!!")
    print(f"This bot is owned by {bot.owner}")


for file in os.listdir("extensions"):
    if file.endswith(".py"):
        file = file.replace(".py", "")
        file = f"extensions.{file}"
        bot.load_extension(file)


bot.start(TOKEN)
