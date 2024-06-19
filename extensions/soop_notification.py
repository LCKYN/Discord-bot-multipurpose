import asyncio
import json
import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv
from interactions import Button, ButtonStyle, Embed, Extension, listen

load_dotenv()
SOOP_TOKEN = os.getenv("SOOP_TOKEN")
GUILD_ID = 1248571511061876838
SOOP_CLIENT_ID = os.getenv("SOOP_CLIENT_ID")


class SoopNotification(Extension):

    def __init__(self, bot):
        self.bot = bot
        self.notification_task = None
        self.username_mapping = {
            "fifatargrean": {
                "target_channel": 1252207765963669545,
                "last_live_status": False,
                "last_send_notification": 0,
            },
        }

    @listen()
    async def on_ready(self):
        print("Soop Notification Ready !!")
        if self.notification_task is None:
            self.notification_task = asyncio.create_task(self.schedule_notifications())

    async def get_soop_live_data(self):
        URL = "https://api.sooplive.com/main/follow"
        HEADERS = {
            "accept": "application/json",
            "authorization": f"Bearer {SOOP_TOKEN}",
            "client-id": SOOP_CLIENT_ID,
        }

        response = requests.request("GET", URL, headers=HEADERS)
        response = json.loads(response.text)
        response_pf = pd.DataFrame(response["getFollowChannelList"])

        for k, v in self.username_mapping.items():

            filtered_df = response_pf[response_pf["channelId"] == k]

            categories = filtered_df["streamCategories"].values[0][0]
            current_status = filtered_df["isStreaming"].values[0]
            display_name = filtered_df["nickname"]
            thumbnail = filtered_df["thumbnailUrl"].values[0]
            title = filtered_df["title"].values[0]
            viewer_count = filtered_df["streamViewerCount"].values[0]

            if not v["last_live_status"] and current_status and time.time() - v["last_send_notification"] > 1200:
                channel = await self.bot.fetch_channel(v["target_channel"])
                components = Button(
                    style=ButtonStyle.LINK,
                    label="Watch Stream",
                    url=f"https://www.sooplive.com/{k}",
                )

                await channel.send(
                    content=f"@everyone {display_name.values[0]} is now live!",
                    embed=Embed(color=0xD2FE2C)
                    .add_field(
                        name=f"{display_name.values[0]} is now live on Soop!",
                        value=f"[{title}](https://www.sooplive.com/{k})",
                    )
                    .add_field(name="Categories", value=categories, inline=True)
                    .add_field(name="Viewers", value=viewer_count, inline=True)
                    .set_image(url=thumbnail),
                    components=[components],
                )

                self.username_mapping[k]["last_send_notification"] = time.time()
            self.username_mapping[k]["last_live_status"] = filtered_df["isStreaming"]

    async def schedule_notifications(self):
        while True:
            await self.get_soop_live_data()
            await asyncio.sleep(240)
