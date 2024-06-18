from interactions import Extension, listen

from src.contains_link import contains_link
from src.spam_detector import SpamDetector

IGNORE_CHANNELS = [940952038991347722, 940966263168065547, 940918622845550612, 980657221845274654, 997121903493914665]


class SpamDetectorWithLink(Extension):

    def __init__(self, bot):
        self.spam_detector = SpamDetector(max_messages=4, time_limit=20)
        self.bot = bot

    @listen()
    async def on_ready(self):
        print("SpamDetectorWithLink Ready !!")

    @listen()
    async def on_message_create(self, event):
        user_id = event.message.author.id
        channel_id = event.message.channel.id
        content = event.message.content
        is_link = contains_link(content)
        is_ignore_channel = channel_id in IGNORE_CHANNELS

        if is_ignore_channel:
            return

        if is_link:
            spam_result = self.spam_detector.add_message(user_id, content, channel_id)
            if spam_result:
                await self.ban_spammer(user_id, channel_id, content)

    async def ban_spammer(self, user_id, channel_id, content):
        channel = await self.client.fetch_channel(channel_id)
        await channel.send(f"ส่งไรจ๊ะ <@{user_id}> แตก!")
        guild = await self.client.fetch_guild(channel.guild.id)
        await guild.ban(
            user_id,
            delete_message_days=1,
            delete_message_seconds=180,
            reason=f"Spamming in channel {channel_id} \nwith message: {content}",
        )


def setup(bot):
    SpamDetectorWithLink(bot)
