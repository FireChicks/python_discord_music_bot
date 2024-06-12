import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
from PIL import Image, ImageDraw, ImageFont
import random

class Ladder(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="사다리",
        description="현재 보이스 채널의 멤버들로 사다리 게임을 시작합니다."
    )
    @app_commands.describe(
        result="결과들을 /으로 구분하여 입력하세요. 예: 결과1/결과2/결과3"
    )
    async def ladder_start(self, interaction: Interaction, result: str) -> None:
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.response.send_message("먼저 보이스 채널에 접속해야 합니다.")
            return

        voice_channel = interaction.user.voice.channel
        participants = [member.display_name for member in voice_channel.members if not member.bot]

        resultList = result.split('/')

        if len(participants) != len(resultList):
            await interaction.response.send_message("보이스 채널의 참가자 수와 결과의 수가 동일해야 합니다.")
            return

        matches = list(zip(participants, random.sample(resultList, len(resultList))))

        imageRoute = self.generate_ladder_image(matches)
        await interaction.response.send_message(file=discord.File(imageRoute))

    @app_commands.command(
        name="게임사다리",
        description="현재 보이스 채널의 멤버들로 사다리 게임을 시작합니다."
    )
    @app_commands.describe(
        game_list="게임들을 /으로 구분하여 입력하세요. 예: 게임1/게임2/게임3"
    )
    async def game_start(self, interaction: Interaction, game_list: str) -> None:
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.response.send_message("먼저 보이스 채널에 접속해야 합니다.")
            return

        voice_channel = interaction.user.voice.channel
        resultList = game_list.split('/')

        winngs = ['당첨']

        while True:
            if len(winngs) != len(resultList):
                winngs.append('꽝')
            else :
                break

        matches = list(zip(winngs, random.sample(resultList, len(resultList))))

        imageRoute = self.generate_ladder_image(matches)
        await interaction.response.send_message(file=discord.File(imageRoute))

    def generate_ladder_image(self, matches):
        # 이미지 크기 설정
        width, height = 500, 50 * len(matches) + 50
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        # 한글 폰트 로드
        font_path = "/python/python_discord_music_bot/font/NanumGothicBold.ttf"  # NanumGothic 폰트 파일 경로
        font = ImageFont.truetype(font_path, 18)  # 폰트 크기 지정 (원하는 크기로 변경하세요)

        # 참가자 이름 및 결과 작성
        for i, (participant, result) in enumerate(matches):
            draw.text((10, 10 + i * 50), f"{participant} -> {result}", fill="black", font=font)

        # 이미지 저장
        image_path = '/tmp/ladder_result.png'
        image.save(image_path)
        return image_path

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        Ladder(bot),
        guilds=[]
    )