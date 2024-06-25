import asyncio
import os
import time
from datetime import datetime

import pytz
import requests
from dotenv import load_dotenv
from interactions import Button, ButtonStyle, Embed, Extension, listen

# Load environment variables
load_dotenv()
SOOP_TOKEN = os.getenv("SOOP_TOKEN")
SOOP_CLIENT_ID = os.getenv("SOOP_CLIENT_ID")
FIFATARGREAN_NOTIFICATION_CHANNEL = int(os.getenv("FIFATARGREAN_NOTIFICATION_CHANNEL"))


class SoopNotification(Extension):

    def __init__(self, bot):
        self.bot = bot
        self.notification_task = None
        self.username_mapping = {
            "fifatargrean": {
                "target_channel": FIFATARGREAN_NOTIFICATION_CHANNEL,
                "last_send_notification": time.time(),
            },
        }

    @listen()
    async def on_ready(self):
        print("Soop Notification Ready !!")
        if self.notification_task is None:
            self.notification_task = asyncio.create_task(self.schedule_notifications())

    async def fetch_json(self, url, headers):
        response = requests.get(url, headers=headers)
        return response.json()

    async def get_stream_info(self, username):
        headers = {
            "accept": "application/json",
            "client-id": SOOP_CLIENT_ID,
        }

        stream_info_url = f"https://api.sooplive.com/stream/info/{username}"
        stream_info = await self.fetch_json(stream_info_url, headers)
        return stream_info

    async def get_stream_data(self, username, stream_data):
        headers = {
            "accept": "application/json",
            "client-id": SOOP_CLIENT_ID,
        }

        url_viewer = f"https://api.sooplive.com/stream/info/{username}/live"
        url_info = f"https://api.sooplive.com/channel/info/{username}"

        response_viewer = await self.fetch_json(url_viewer, headers)
        response_info = await self.fetch_json(url_info, headers)

        display_name = response_info["streamerChannelInfo"]["nickname"]
        start_time = datetime.strptime(stream_data["streamStartDate"], "%Y-%m-%dT%H:%M:%S.%fZ")
        utc_zone = pytz.utc
        thailand_zone = pytz.timezone("Asia/Bangkok")

        start_time = utc_zone.localize(start_time)
        thailand_time = start_time.astimezone(thailand_zone)

        return {
            "display_name": display_name,
            "category": "Just Chatting",  # Stream data category hardcoded as "Just Chatting"
            "language": stream_data["languageCode"],
            "start_time": thailand_time.timestamp(),
            "thumbnail": f"https://api.sooplive.com/media/live/{username}/thumbnail.jpg",
            "title": stream_data["title"],
            "viewer_count": response_viewer["viewer"],
        }

    async def send_notification(self, username, stream_data):
        target_channel = self.username_mapping[username]["target_channel"]
        channel = await self.bot.fetch_channel(target_channel)

        components = Button(
            style=ButtonStyle.LINK,
            label="Watch Stream",
            url=f"https://www.sooplive.com/{username}",
        )

        await channel.send(
            content=f"@everyone {stream_data['display_name']} is now live!",
            embed=Embed(color=0xD2FE2C)
            .add_field(
                name=f"{stream_data['display_name']} is now live on Soop!",
                value=f"[{stream_data['title']}](https://www.sooplive.com/{username})",
            )
            .add_field(name="Categories", value=stream_data["category"], inline=True)
            .add_field(name="Viewers", value=stream_data["viewer_count"], inline=True)
            .set_image(url=stream_data["thumbnail"]),
            components=[components],
        )

    async def get_soop_live_data(self):
        for username in self.username_mapping:
            stream_info = await self.get_stream_info(username)
            if stream_info["isStream"]:
                stream_data = await self.get_stream_data(username, stream_info["data"])
                print(self.username_mapping[username]["last_send_notification"] - stream_data["start_time"])
                if self.username_mapping[username]["last_send_notification"] < stream_data["start_time"]:
                    await self.send_notification(username, stream_data)
                    self.username_mapping[username]["last_send_notification"] = time.time()

            await asyncio.sleep(1)

    async def schedule_notifications(self):
        while True:
            await self.get_soop_live_data()
            await asyncio.sleep(240)
