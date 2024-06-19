from interactions import (
    Button,
    ButtonStyle,
    Embed,
    Extension,
    SlashContext,
    listen,
    slash_command,
)

# # Real values
# MOD_ROLE = [939703911558840331]
# COMMAND_CHANNEL = 956301076271857764
# TARGET_CHANNEL = 940247837575368754
# GUILD_ID = 939695971384844338

# test values
MOD_ROLE = [1252932199204917300]
COMMAND_CHANNEL = 1248571511061876841
TARGET_CHANNEL = 1252207765963669545
GUILD_ID = 1248571511061876838


class SoopManualNotification(Extension):

    def __init__(self, bot):
        self.bot = bot

    @listen()
    async def on_ready(self):
        print("Soop Manual Notification Ready !!")

    @slash_command(
        name="streamstart",
        description="send notification to everyone",
        scopes=[
            GUILD_ID,
        ],
    )
    async def streamstart(self, ctx: SlashContext):
        have_mod_role = any(role.id in MOD_ROLE for role in ctx.author.roles)
        from_command_channel = ctx.channel_id == COMMAND_CHANNEL

        if not have_mod_role or not from_command_channel:
            await ctx.send(
                embed=Embed(
                    title="You don't have permission to use this command or you are not in the correct channel!",
                    color=0xFF0000,
                )
                .add_field(
                    name="Permission",
                    value=f"MOD role required, you have {'MOD role' if have_mod_role else 'no MOD role'}",
                )
                .add_field(
                    name="Channel",
                    value=f"Command must be used in <#{COMMAND_CHANNEL}>, you are in <#{ctx.channel_id}>",
                ),
                ephemeral=True,
            )
            return

        channel = await self.bot.fetch_channel(TARGET_CHANNEL)
        components = Button(
            style=ButtonStyle.LINK,
            label="Watch Stream",
            url="https://www.sooplive.com/fifatargrean",
        )
        await channel.send(
            content="@everyone FifaTargrean is now live!",
            embed=Embed(color=0xD2FE2C)
            .add_field(
                name="FifaTargrean is now live on Soop!",
                value="https://www.sooplive.com/fifatargrean",
            )
            .add_image(
                image="https://static.sooplive.com/image/channel/profile/fifatargrean.png?random=b7c7a25c4e67",
            ),
            components=components,
        )

        await ctx.send("Notification sent!", ephemeral=True)
