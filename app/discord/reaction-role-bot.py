import discord
from discord.ext import commands

from app.config.settings import Settings
from app.utils.logger import setup_logger

settings = Settings()
logger = setup_logger("Discord Bot")


class Client(commands.Bot):
    color_roles_message_id: int | None = None

    async def on_ready(self):
        print(f"Logged on as {self.user}!")

        try:
            guild = discord.Object(id=settings.DISCORD_SERVER_ID)
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} commands to guild {guild.id}")

        except discord.HTTPException:
            logger.error("Error syncing commands")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith("hello"):
            await message.channel.send(f"Hello there {message.author}")

    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        guild = reaction.message.guild
        if not guild:
            return

        if self.color_roles_message_id is not None and reaction.message.id != self.color_roles_message_id:
            return

        emoji = str(reaction.emoji)

        reaction_role_map = {
            "❤️": "Red",
            "💙": "Blue",
            "💛": "Yellow",
            "💚": "Green",
            "🧡": "Orange",
        }

        if emoji in reaction_role_map:
            role_name = reaction_role_map[emoji]
            role = discord.utils.get(guild.roles, name=role_name)

            if role and user:
                await user.add_roles(role)
                print(f"Assigned {role_name} to {user}")

    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return

        guild = reaction.message.guild
        if not guild:
            return

        if self.color_roles_message_id is not None and reaction.message.id != self.color_roles_message_id:
            return

        emoji = str(reaction.emoji)

        reaction_role_map = {
            "❤️": "Red",
            "💙": "Blue",
            "💛": "Yellow",
            "💚": "Green",
            "🧡": "Orange",
        }

        if emoji in reaction_role_map:
            role_name = reaction_role_map[emoji]
            role = discord.utils.get(guild.roles, name=role_name)

            if role and user:
                await user.remove_roles(role)
                print(f"Removed {role_name} to {user}")


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True
client = Client(command_prefix="!", intents=intents)

GUILD_ID = discord.Object(id=settings.DISCORD_SERVER_ID)


@client.tree.command(name="hello", description="Say hello", guild=GUILD_ID)
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello there")


@client.tree.command(
    name="colourroles",
    description="Create a message that lets users pick a colour role",
    guild=GUILD_ID,
)
async def color_roles(interaction: discord.Interaction):
    if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "You must be an admin to run this command", ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    description = (
        "React to this message to get your color role!\n\n"
        "❤️ Red\n"
        "💙 Blue\n"
        "💛 Yellow\n"
        "💚 Green\n"
        "🧡 Orange\n"
    )

    embed = discord.Embed(
        title="Pick you Color", description=description, color=discord.Color.blurple()
    )

    channel = interaction.channel
    if not isinstance(channel, (discord.TextChannel, discord.Thread, discord.VoiceChannel, discord.StageChannel)):
        await interaction.followup.send(
            "This command can't be used in this channel type.", ephemeral=True
        )
        return

    message = await channel.send(embed=embed)

    emojis = ["❤️", "💙", "💛", "💚", "🧡"]

    for emoji in emojis:
        await message.add_reaction(emoji)

    client.color_roles_message_id = message.id

    await interaction.followup.send("Colour role message created!", ephemeral=True)


client.run(settings.DISCORD_BOT_TOKEN)
