import discord
from discord.ext import commands, tasks
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=discord.Intents.all(),
            sync_command=True,
            application_id=ET.parse('bot_account.xml').getroot().find('bot_id').text,  # botID
            help_command=commands.DefaultHelpCommand()  # help_command 설정
        )
        self.initial_extension = [
            "Cogs.hello",
            "Cogs.music",
            "Cogs.ladder"  # tts 코그 추가
        ]
        self.channel_last_activity = {}  # 채널별 마지막 입장 시간 저장
        self.inactivity_check.start()  # 비활동 체크 시작

    async def setup_hook(self):
        for ext in self.initial_extension:
            await self.load_extension(ext)
        await self.tree.sync()

    async def on_ready(self):
        print("login")
        print(self.user.name)
        print(self.user.id)
        print("===============")
        game = discord.Game("테스트")
        await self.change_presence(status=discord.Status.online, activity=game)

    async def on_member_update(self, before, after):
        # 사용자가 채팅방에 입장했을 때 기록
        if before.guild == after.guild:
            # 채널에 새로운 사용자가 입장한 경우
            for channel in after.guild.text_channels:
                if channel.id not in self.channel_last_activity:
                    # 채널에 입장한 적이 없다면
                    self.channel_last_activity[channel.id] = datetime.utcnow()
                    print(f"채널 {channel.name}에 입장 기록: {self.channel_last_activity[channel.id]}")
                elif after in channel.members:
                    # 채널에 새로운 사람이 입장했을 때
                    self.channel_last_activity[channel.id] = datetime.utcnow()
                    print(f"채널 {channel.name}에 입장 기록 갱신: {self.channel_last_activity[channel.id]}")

    # 10분 마다 활동이 없던 채널을 체크하고 퇴장
    @tasks.loop(minutes=10)
    async def inactivity_check(self):
        current_time = datetime.utcnow()
        for channel_id, last_activity in list(self.channel_last_activity.items()):
            if (current_time - last_activity) > timedelta(minutes=10):
                # 10분 이상 활동이 없으면 퇴장
                channel = self.get_channel(channel_id)
                if channel:
                    print(f"채팅방 {channel.name}에서 10분 동안 활동이 없어 퇴장합니다.")
                    await channel.guild.leave()  # 서버를 떠나게 함
                    del self.channel_last_activity[channel_id]  # 활동 기록 삭제

    @inactivity_check.before_loop
    async def before_inactivity_check(self):
        await self.wait_until_ready()


bot = MyBot()
bot.run(ET.parse('bot_account.xml').getroot().find('token').text)  # 봇 토큰
