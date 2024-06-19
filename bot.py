import os

from dotenv import load_dotenv
from interactions import Activity, ActivityType, Client, Intents, PartialEmoji, listen

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN_TEST")

bot = Client(
    intents=Intents.ALL | Intents.MESSAGE_CONTENT,
    activity=Activity(
        "with spaghetti code",
        type=ActivityType.PLAYING,
        details="If I do something wrong, please tell me (LCKYN).\nPlease don't send DM to me",
    ),
)


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
