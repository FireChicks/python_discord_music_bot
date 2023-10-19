from discord.ext import commands
from discord import app_commands
from discord import Message
from discord import Object
from discord import FFmpegPCMAudio
from discord.ui import Button, View
from discord import ButtonStyle
from gtts import gTTS
from discord import Interaction
import os
import queue

class tts(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.language = "ko"  # language를 tts 클래스의 속성으로 변경
        self.target_channel_id = 1129740733008588901  # tts 채널
        self.queue = queue.Queue()

        # tts 디렉토리가 없으면 생성합니다.
        if not os.path.exists("tts"):
            os.makedirs("tts")

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.channel.id != self.target_channel_id:
            return  # 봇 메시지이거나 특정 채널이 아닌 경우 무시합니다.

        content = message.content  # 메시지의 내용을 가져옵니다.
        print(content+'를 TTS를 사용해서 말합니다.')
        tts = gTTS(text=content, lang=self.language)  # self.language 사용
        file_name = f'tts/voice_{message.id}.mp3'  # 메시지 ID를 포함한 고유한 음성 파일 이름
        tts.save(file_name)

        # 음성 파일을 큐에 추가합니다.
        self.queue.put(file_name)
        print(self.queue.get())

        # 큐가 비어있으면 재생을 시작합니다.
        if self.queue.qsize() == 1:
            await self.play_next_message(message.guild)

    async def play_next_message(self, guild):
        if self.queue:
            file_name = self.queue.get()
            voice_channel = guild.me.voice.channel
            voice_client = guild.voice_client

            if voice_channel:
                if not voice_client or not voice_client.is_connected():
                    voice_client = await voice_channel.connect()

                def after_play(error):
                    if error:
                        print(f"오류 발생: {error}")

                    if self.queue:
                        file_name = self.queue.get()
                        source = FFmpegPCMAudio(file_name)
                        voice_client.play(source, after=after_play)  # 수정된 부분

                source = FFmpegPCMAudio(file_name)
                voice_client.play(source, after=after_play)  # 수정된 부분
            else:
                self.queue = queue.Queue()
                await guild.text_channels[0].send("음성 채널에 연결되어 있지 않습니다.")

    async def after_play(self,guild, error):
        if error:
            print(f"오류 발생: {error}")

        # 재생이 끝난 음성 파일을 제거하고 다음 메시지를 재생합니다.
        file_name = self.queue.get()
        if self.queue:
            voice_client = guild.voice_client
            source = FFmpegPCMAudio(file_name)
            voice_client.play(source, after=lambda e: self.after_play(e))
        else:
            # 큐가 비어있으면 Bot을 음소거 해제합니다.
            guild.me.edit(deafen=False)

    @app_commands.command(
        name="메뉴",
        description="메뉴를 표시합니다."
    )
    async def menu(self, interaction: Interaction) -> None:
        btnKor = Button(label="한국어", style=ButtonStyle.primary)
        btnJap = Button(label="일본어", style=ButtonStyle.primary)
        btnEng = Button(label="영어", style=ButtonStyle.primary)
        btnDeu = Button(label="독일어", style=ButtonStyle.primary)

        async def btn_kor_callback(interaction: Interaction):
            self.language = "ko"  # 언어 설정 변경
            await interaction.channel.send("한국어로 설정을 변경하였습니다.")

        async def btn_jap_callback(interaction: Interaction):
            self.language = "ja"  # 언어 설정 변경
            await interaction.channel.send("일본어로 설정을 변경하였습니다.")

        async def btn_eng_callback(interaction: Interaction):
            self.language = "en"  # 언어 설정 변경
            await interaction.channel.send("영어로 설정을 변경하였습니다.")

        async def btn_deu_callback(interaction: Interaction):
            self.language = "de"  # 언어 설정 변경
            await interaction.channel.send("독일어로 설정을 변경하였습니다.")

        btnKor.callback = btn_kor_callback
        btnJap.callback = btn_jap_callback
        btnEng.callback = btn_eng_callback
        btnDeu.callback = btn_deu_callback
        view = View()

        view.add_item(btnKor)
        view.add_item(btnJap)
        view.add_item(btnEng)
        view.add_item(btnDeu)
        await interaction.response.send_message("옵션을 선택해주세요.", view=view)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        tts(bot),
        guilds=[]
    )
