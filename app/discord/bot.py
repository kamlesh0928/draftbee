import discord

from app.config.settings import Settings


class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('hello'):
            await message.channel.send(f'Hello there {message.author}!')


intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run(Settings.DISCORD_BOT_TOKEN)
