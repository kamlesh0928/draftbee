import discord
from discord.ext import commands

from app.config.settings import Settings
from app.utils.logger import Logger

settings = Settings()
logger = Logger()


class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged on as {self.user}")

        try:
            guild = discord.Object(id=settings.DISCORD_SERVER_ID)
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} command(s) to the guild.")

        except discord.HTTPException:
            logger.exception("Error syncing commands")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith("hello"):
            await message.channel.send(f"Hello there {message.author}!")


class Menu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Up", description="Move up", emoji="⬆️"),
            discord.SelectOption(label="Down", description="Move Down", emoji="⬇️"),
            discord.SelectOption(label="Left", description="Move Left", emoji="⬅️"),
            discord.SelectOption(label="Right", description="Move Right", emoji="➡️"),
        ]

        super().__init__(
            placeholder="Choose an option:", min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Up":
            await interaction.response.send_message("Moved up")
        elif self.values[0] == "Down":
            await interaction.response.send_message("Moved down")
        elif self.values[0] == "Left":
            await interaction.response.send_message("Moved left")
        else:
            await interaction.response.send_message("Moved right")


class MenuView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Menu())


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

GUILD_ID = discord.Object(id=settings.DISCORD_SERVER_ID)


@client.tree.command(
    name="menu", description="Displaying a drop down menu", guild=GUILD_ID
)
async def menu(interaction: discord.Interaction):
    await interaction.response.send_message(view=MenuView())


client.run(settings.DISCORD_BOT_TOKEN)
