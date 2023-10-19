from discord import Member
from discord import VoiceChannel
from discord.ext import commands
from discord import app_commands
from discord import Interaction

class join(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="입장",
        description="봇을 입장시킵니다."
    )
    async def join(self, interaction: Interaction) -> None:
        member: Member = interaction.user  # Interaction에서 Member 객체 가져오기
        voice_channel: VoiceChannel = member.voice.channel  # 사용자가 접속한 음성 채널 가져오기

        voice_client = interaction.guild.voice_client

        if voice_client is not None and voice_client.is_connected():
            await voice_client.move_to(voice_channel)
        else:
            voice_client = await voice_channel.connect()

        await interaction.response.send_message("보이스채널에 입장합니다")
        print("bot이 " + voice_channel.name + "에 입장하였습니다.")

    @app_commands.command(
        name="퇴장",
        description="봇을 퇴장시킵니다."
    )
    async def exit(self, interaction: Interaction) -> None:
        member: Member = interaction.user  # Interaction에서 Member 객체 가져오기
        voice_channel: VoiceChannel = member.voice.channel  # 사용자가 접속한 음성 채널 가져오기

        voice_client = interaction.guild.voice_client

        if voice_client is not None and voice_client.is_connected():
            await voice_client.disconnect()
            await interaction.response.send_message("보이스채널에서 퇴장합니다")
            print("bot이 " + voice_channel.name + "에서 퇴장하였습니다.")
        else:
            await interaction.response.send_message("보이스채널에 연결되어 있지 않습니다")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        join(bot),
        guilds=[]
    )
