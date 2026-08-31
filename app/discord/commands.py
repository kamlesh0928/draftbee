import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()


class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

        try:
            guild = discord.Object(id=os.getenv('DISCORD_SERVER_ID'))
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} command(s) to the guild.')

        except Exception as e:
            print(f'Error syncing commands: {e}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('hello'):
            await message.channel.send(f'Hello there {message.author}!')


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix='!', intents=intents)

GUILD_ID = discord.Object(id=os.getenv('DISCORD_SERVER_ID'))

@client.tree.command(name='embeds', description='I will print what you write', guild=GUILD_ID)
async def embeds(interaction: discord.Interaction):
    embed = discord.Embed(title='I am a Title', description='I am description')
    await interaction.response.send_message(embed=embed)

client.run(os.getenv('DISCORD_BOT_TOKEN'))
