from interactions import Embed, Extension, listen

from src.contains_link import contains_link
from src.spam_detector import SpamDetector

IGNORE_CHANNELS = [
    940952038991347722,
    940966263168065547,
    940918622845550612,
    980657221845274654,
    997121903493914665,
]


class SpamDetectorWithLink(Extension):

    def __init__(self, bot):
        self.spam_detector = SpamDetector(max_messages=4, time_limit=30)
        self.bot = bot

    @listen()
    async def on_ready(self):
        print("Spam Detector With Link Ready !!")

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
                await self.ban_spammer(user_id, channel_id, content, spam_result["all_messages"])

    async def ban_spammer(self, user_id, channel_id, content, all_messages):
        channel = await self.client.fetch_channel(channel_id)
        embed = (
            Embed(color=0xFF0000)
            .add_field(name="Ban user", value=f"ส่งไรจ๊ะ <@{user_id}> แตก!")
            .add_field(name="Ban reason", value=all_messages)
            .add_image(image="https://media.tenor.com/SJ2HvoNKCwkAAAAi/pepe-the-frog-pepe.gif")
            .add_field(name="Owner", value=f"<@{self.bot.owner.id}>")
        )

        guild = await self.client.fetch_guild(channel.guild.id)
        await guild.ban(
            user_id,
            delete_message_days=1,
            delete_message_seconds=60 * 30,
            reason=f"Spamming in channel {channel_id} \nwith message: {content}",
        )

        await channel.send(embed=embed)
        await self.bot.owner.send(embed=embed)


def setup(bot):
    SpamDetectorWithLink(bot)
