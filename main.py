from discord.ext import commands
from discord import Intents
from discord import Game
from discord import Status
from discord import Object
import queue
import xml.etree.ElementTree as ET


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=Intents.all(),
            sync_command=True,
            application_id= ET.parse('bot_account.xml').getroot().find('bot_id').text,         # botID
            help_command=commands.DefaultHelpCommand()  # help_command 설정
        )
        self.initial_extension = [
            "Cogs.hello",
            "Cogs.music"# tts 코그 추가
        ]
        self.queue = queue.Queue()

    async def setup_hook(self):
        for ext in self.initial_extension:
            await self.load_extension(ext)
        await self.tree.sync()

    async def on_ready(self):
        print("login")
        print(self.user.name)
        print(self.user.id)
        print("===============")
        game = Game("테스트")
        await self.change_presence(status=Status.online, activity=game)


bot = MyBot()
bot.run(ET.parse('bot_account.xml').getroot().find('token').text) #봇 토큰
