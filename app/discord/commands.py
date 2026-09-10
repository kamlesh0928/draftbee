import discord
from discord.ext import commands

from app.config.settings import Settings
from app.utils.logger import setup_logger

settings = Settings()
logger = setup_logger("Discord Bot")


class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged on as {self.user}")

        try:
            guild = discord.Object(id=settings.DISCORD_SERVER_ID)
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} command(s) to the guild.")

        except discord.HTTPException:
            logger.error("Error syncing commands")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith("hello"):
            await message.channel.send(f"Hello there {message.author}!")


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

GUILD_ID = discord.Object(id=settings.DISCORD_SERVER_ID)


@client.tree.command(name="hello", description="Say hello to the bot", guild=GUILD_ID)
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello!")


@client.tree.command(
    name="printer", description="I will print what you write", guild=GUILD_ID
)
async def printer(interaction: discord.Interaction, printer: str):
    await interaction.response.send_message(printer)


client.run(settings.DISCORD_BOT_TOKEN)
