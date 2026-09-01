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


class View(discord.ui.View):
    @discord.ui.button(label='Click Me!', style=discord.ButtonStyle.blurple, emoji='👋')
    async def button_callback_1(self, button, interaction):
        await button.response.send_message(f'You clicked the button1.')

    @discord.ui.button(label='Press Me!', style=discord.ButtonStyle.red, emoji='💀')
    async def button_callback_2(self, button, interaction):
        await button.response.send_message(f'You clicked the button2.')

    @discord.ui.button(label='Tap Me!', style=discord.ButtonStyle.green, emoji='🔥')
    async def button_callback_3(self, button, interaction):
        await button.response.send_message(f'You clicked the button3.')


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix='!', intents=intents)

GUILD_ID = discord.Object(id=os.getenv('DISCORD_SERVER_ID'))

@client.tree.command(name='button', description='Displaying a button', guild=GUILD_ID)
async def button(interaction: discord.Interaction):
    await interaction.response.send_message(view=View())

client.run(os.getenv('DISCORD_BOT_TOKEN'))
