import discord
from discord.ext import commands

from app.config.settings import Settings

settings = Settings()


class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

        try:
            guild = discord.Object(id=settings.DISCORD_SERVER_ID)
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

GUILD_ID = discord.Object(id=settings.DISCORD_SERVER_ID)

@client.tree.command(name='embeds', description='I will print what you write', guild=GUILD_ID)
async def embeds(interaction: discord.Interaction):
    embed = discord.Embed(title='I am a Title', url='https://github.com/kamlesh0928', description='I am description', color=discord.Color.blue())
    embed.set_thumbnail(url='https://avatars.githubusercontent.com/u/12345678?v=4')
    embed.add_field(name='Field 1', value='This is the value of field 1', inline=False)
    embed.add_field(name='Field 2', value='This is the value of field 2')
    embed.set_footer(text='This is the footer text')
    embed.set_author(name=interaction.user.name, url='https://github.com/kamlesh0928')
    await interaction.response.send_message(embed=embed)

client.run(settings.DISCORD_BOT_TOKEN)
