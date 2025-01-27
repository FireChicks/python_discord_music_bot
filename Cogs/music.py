import queue
import random
import time
import discord
from functools import partial
from discord import Member
from discord import VoiceChannel
from discord import app_commands
from discord import Interaction
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord import Message
from discord.ui import Button, View
from discord import ButtonStyle
import asyncio
import yt_dlp
import os
import music_sub as sub

class music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.target_channel_id = 789084495584165899  # 명령어를 받을 채널
        self.queue = queue.Queue()
        self.now_music_name = ''
        self.found_files = []
        self.volume = 50
        self.isRandomAppend = False

        self.downloadPath = "downloads/"
        #self.ffmpegPath = "C:\Program Files/ffmpeg-6.0-full_build/bin/ffmpeg.exe"
        self.ffmpegPath = "/usr/bin/ffmpeg"

        if not os.path.exists("tts"):
            os.makedirs("tts")
        if not os.path.exists("downloads/"):
            os.makedirs("downloads/")

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

        # 보이스 채널에 사람이 없으면 10분 후에 나가도록 설정
        await self.monitor_voice_channel(voice_client, voice_channel)

    async def monitor_voice_channel(self, voice_client, voice_channel: VoiceChannel) -> None:
        while voice_client.is_connected():
            # 봇을 제외한 사람 확인
            members_in_channel = sum(1 for member in voice_channel.members if not member.bot)
            print(f"체크실시, 현재 사람 수: {members_in_channel}")

            # 만약 채널에 사람이 없다면
            if members_in_channel == 0:
                print(f"채널에 사람이 없으므로 10분 뒤에 나갑니다.")
                await asyncio.sleep(600)  # 10분 동안 대기 (600초)

                # 10분 후에도 여전히 채널에 사람이 없다면 나가기
                if sum(1 for member in voice_channel.members if not member.bot) == 0:
                    await voice_client.disconnect()
                    print(f"보이스 채널에서 나갔습니다. ({voice_channel.name})")
                    break

            # 주기적으로 확인 (1분마다 체크)
            await asyncio.sleep(60)

    @app_commands.command(
        name="퇴장",
        description="봇을 퇴장시킵니다."
    )
    async def exit(self, interaction: Interaction) -> None:
        member: Member = interaction.user  # Interaction에서 Member 객체 가져오기
        voice_channel: VoiceChannel = member.voice.channel  # 사용자가 접속한 음성 채널 가져오기

        voice_client = interaction.guild.voice_client
        voice_client.stop()

        self.clear_playList()

        if voice_client is not None and voice_client.is_connected():
            await voice_client.disconnect()
            await interaction.response.send_message("보이스채널에서 퇴장합니다")
            print("bot이 " + voice_channel.name + "에서 퇴장하였습니다.")
        else:
            await interaction.response.send_message("보이스채널에 연결되어 있지 않습니다")

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.channel.id != self.target_channel_id:
            return  # 봇 메시지이거나 특정 채널이 아닌 경우 무시합니다.

        voice_channel = message.guild.me.voice.channel
        voice_client = message.guild.voice_client

        if voice_client is not None and voice_client.is_connected():
            await voice_client.move_to(voice_channel)
        else:
            voice_client = await voice_channel.connect()

        await self.insert_music(message)

    async def insert_music(self, message):

        voice_channel = message.guild.me.voice.channel
        voice_client = message.guild.voice_client

        url = ''
        if message.content.startswith("https://www.youtube.com/watch?v="): #URL 파싱
            url = message.content.split("https://www.youtube.com/watch?v=")[1]
        elif message.content.startswith("https://youtu.be/"):
            url = message.content.split("https://youtu.be/")[1]

        # 이미 있던 링크라서 재생시간이 들어있을 경우
        if "&t=" in url:
            split_result = url.split("&t=")
            url = split_result[0]

        if "?si=" in url:
            split_result = url.split("?si=")
            url = split_result[0]

        option = {
            'format': 'bestaudio/best',
            'outtmpl': "downloads/%(id)s",  # 다운로드 디렉토리와 파일명 형식을 설정합니다.
            'yes-playlist': False,
            'ignoreerrors': True,
            'nooverwrites': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'verbose': 0  # 자세한 로그를 출력합니다.
        }
        try:
            with yt_dlp.YoutubeDL(option) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=False)
                title = sub.sanitize_filename(info["title"] + ".mp3")
                fileName = info["id"] + ".mp3"
                await message.channel.send("**" + title + "** 을 플레이리스트에 추가하겠습니다")
                isAvailable = True

                for realfilename in os.listdir(self.downloadPath):
                    if realfilename == title:
                        isAvailable = False
                        print("이미 다운로드되어 있는 노래입니다.")

                if isAvailable:
                    await asyncio.to_thread(ydl.download, [url])  # 파일을 다운로드합니다.
                    await asyncio.to_thread(sub.rename_files, self.downloadPath, fileName, title)  # id로 된 파일명 변경
            queue_part = {'path': self.downloadPath + title, 'author': message.author}
            self.queue.put(queue_part)  # 플레이리스트에 노래 파일명, 추가한 사람 추가
            await message.channel.send("**" + title + "** 을 성공적으로 플레이리스트에 추가하였습니다")

            if self.queue.qsize() == 1 and not voice_client.is_playing():  # 큐가 비어있으면 재생 시작
                await self.play_next_music(message.guild)


        except yt_dlp.utils.DownloadError as e:
            await message.channel.send("오류가 발생했습니다. 자세한 로그를 확인하세요.")
            print(f"다운로드 오류: {e}")

    async def play_next_music(self, guild):
        voice_channel = guild.me.voice.channel
        voice_client = guild.voice_client
        if voice_client is not None and voice_client.is_connected():
            await voice_client.move_to(voice_channel)
        else:
            voice_client = await voice_channel.connect()

        if not self.queue.empty():
            if voice_client.is_playing():
                voice_client.stop()
                print('노래 정지')
                return
            que = self.queue.get()
            # 신청한 사람
            name = str(que['author'])
            # 노래 이름
            music_name = que['path']

            if voice_channel:  # 채널 연결여부 확인
                def after_play(error):
                    if error:
                        print(f"오류 발생: {error}")

                    if self.queue.empty() and self.isRandomAppend:
                        self.found_files = self.search_random_music(1)
                        for file_name in self.found_files:
                            queue_part = {'path': self.downloadPath + file_name, 'author': '랜덤 추가'}
                            self.queue.put(queue_part)

                    if not self.queue.empty():
                        music_name = self.queue.get()['path']
                        source = discord.PCMVolumeTransformer(FFmpegPCMAudio(music_name))
                        self.now_music_name = music_name
                        voice_client.play(source, after=after_play)
                        voice_client.source.volume = self.volume / 100
                    else:
                        print('모든 노래 재생 완료')

                source = discord.PCMVolumeTransformer(FFmpegPCMAudio(music_name))
                self.now_music_name = music_name
                voice_client.play(source, after=after_play)
                voice_client.source.volume = self.volume / 100
                await self.send_music_info("**"+name+"**님이 신청한 총 **"
                                                + str(self.queue.qsize() + 1) +"**개의 곡 중 **"
                                                + str(music_name).split('/')[1].split('.')[0] +"**의 재생을 시작하겠습니다.")
            else:
                self.queue = queue.Queue()

    async def send_music_info(self, str):
        target_channel = self.bot.get_channel(self.target_channel_id)
        await target_channel.send(str)

    def makePlayList(self):
        count = 0
        table = ''

        if not self.queue.empty():
            maxLength = 0
            temp_play_list = ''
            for i in self.queue.queue:
                count += 1
                temp_play_list += f'{count}. **{str(i["path"]).split("/")[1].split(".")[0]}**/ *{str(i["author"])}*\n'
                if len(temp_play_list) > maxLength:
                    maxLength = len(temp_play_list)

            table = '플레이리스트를 출력합니다.\n'

            # |---------------------| 최대크기만큼 생성 코드
            tempStr = '|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|\n'

            table += tempStr         # |---------------------|
            table += temp_play_list  # |1.노래명        |추가자|
            table += tempStr         # |---------------------|

        if self.now_music_name:
            table += f'====> 현재 재생중인 노래 : **{self.now_music_name.split("/")[1].split(".")[0].strip(".mp3")}**'
        else:
            table += '현재 재생중인 노래가 없습니다.\n'

        return table

    def change_volume(self, num):
        tempNum = self.volume + num
        if tempNum < 0:
           self.volume = 0
           return 0.0
        elif tempNum > 100:
            self.volume = 100
        else:
            self.volume = tempNum

        return self.volume / 100.0

    def search_music(self, searchText):
        found_files = []
        if searchText:
            index = 0
            found_files.clear()
            for filename in os.listdir(self.downloadPath):
                if filename.upper().find(searchText.upper()) != -1:
                    found_files.append((index, filename))
                    index += 1

        return found_files

    def search_random_music(self, count):
        found_files = []

        if count > 0:
            all_files = os.listdir(self.downloadPath)

            # Shuffle the list of files randomly
            random.shuffle(all_files)

            # Ensure count does not exceed the total number of files
            count = min(count, len(all_files))

            # Add the first 'count' filenames to found_files
            found_files.extend(all_files[:count])

        return found_files

    def clear_playList(self):
        is_empty = True
        while(is_empty):
            if not self.queue.empty():
                self.queue.get()
            else:
                is_empty = False
        self.now_music_name = ''
        self.volume = 50

    @app_commands.command(
        name="플레이리스트",
        description="현재 추가되어있는 노래들을 출력합니다."
    )
    async def show_playlist(self, interaction: Interaction) -> None:
        member: Member = interaction.user  # Interaction에서 Member 객체 가져오기
        voice_channel: VoiceChannel = member.voice.channel  # 사용자가 접속한 음성 채널 가져오기

        table = self.makePlayList()

        voice_client = interaction.guild.voice_client
        await interaction.response.send_message(table)

    @app_commands.command(
        name="초기화",
        description="현재 추가되어있는 노래들을 초기화합니다."
    )
    async def reset_playlist(self, interaction: Interaction) -> None:
        member: Member = interaction.user  # Interaction에서 Member 객체 가져오기
        voice_channel: VoiceChannel = member.voice.channel  # 사용자가 접속한 음성 채널 가져오기

        voice_client = interaction.guild.voice_client
        voice_client.stop()

        self.clear_playList()

        target_channel = self.bot.get_channel(self.target_channel_id)
        await target_channel.send("플레이리스트를 초기화 했습니다.")


    @commands.command()
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @app_commands.command(
        name="search",
        description="다운로드 받은 노래들을 검색합니다."
    )
    async def search_music_by_btn(self, interaction: discord.Interaction, search_text: str) -> None:
        if len(search_text) != 0:
            # user_input을 사용하여 검색 로직을 구현
            # 예: 검색 결과를 user_input을 기반으로 가져옴
            self.found_files = self.search_music(search_text)
            if len(self.found_files) != 0:
                view = discord.ui.View()
                for i in self.found_files:
                    btnSong = Button(label=i[1], style=ButtonStyle.gray)

                    async def btn_song_callback(interaction: Interaction, songName):
                        member: Member = interaction.user
                        voice_channel: VoiceChannel = member.voice.channel
                        voice_client = interaction.guild.voice_client

                        queue_part = {'path': self.downloadPath + songName, 'author': interaction.user.name}
                        self.queue.put(queue_part)
                        await interaction.response.send_message("성공적으로 노래 **" + songName + "**를 추가하였습니다.")

                        if self.queue.qsize() == 1 and not voice_client.is_playing():  # 큐가 비어있으면 재생 시작
                            await self.play_next_music(interaction.guild)
                    btnSong.callback = partial(btn_song_callback, songName = i[1])
                    view.add_item(btnSong)
                await interaction.response.send_message(f"**{search_text}**의 검색 결과.", view=view)
            else:
                await interaction.response.send_message("검색 결과가 없습니다.")
        else:
            await interaction.response.send_message("검색어를 제공하지 않았습니다. 검색어를 입력하세요.")

    @app_commands.command(
        name="autoplay",
        description="랜덤으로 노래를 계속 재생할지 여부를 변경합니다."
    )
    async def flip_auto_play(self, interaction: discord.Interaction) -> None:
            member: Member = interaction.user
            voice_channel: VoiceChannel = member.voice.channel
            voice_client = interaction.guild.voice_client

            if not self.isRandomAppend:  # 큐가 비어있으면 재생 시작
                self.isRandomAppend = True
                await interaction.response.send_message("이제 노래가 비었을 때 랜덤으로 노래를 재생합니다.")
            else:
                self.isRandomAppend = False
                await interaction.response.send_message("이제 노래가 비었을 때 랜덤으로 노래를 재생하지 않습니다.")



    @app_commands.command(
        name="다음",
        description="다음 노래를 재생합니다."
    )
    async def next_music(self, interaction: Interaction) -> None:
        member: Member = interaction.user  # Interaction에서 Member 객체 가져오기
        voice_channel: VoiceChannel = member.voice.channel  # 사용자가 접속한 음성 채널 가져오기

        voice_client = interaction.guild.voice_client
        if self.queue.qsize() > 0:
            await self.play_next_music(interaction.guild)
        else :
            if self.isRandomAppend:
                self.found_files = self.search_random_music(1)
                for file_name in self.found_files:
                    queue_part = {'path': self.downloadPath + file_name, 'author': '랜덤 추가'}
                    self.queue.put(queue_part)
                    await self.play_next_music(interaction.guild)

            await interaction.response.send_message("현재 플레이리스트에 다음 노래가 없습니다.")
        await interaction.response.send_message("다음 노래를 시작합니다.")

    @app_commands.command(
        name="random",
        description="랜덤으로 노래를 추가합니다."
    )
    async def random_append_music(self, interaction: discord.Interaction, input_count: str) -> None:
        try:
            count = int(input_count)
        except ValueError as e:
            await interaction.response.send_message("추가할 노래의 개수를 입력해주세요.")
            count = 0
        if 30 >= count and count > 0:

            self.found_files = self.search_random_music(count)
            member: Member = interaction.user
            voice_channel: VoiceChannel = member.voice.channel
            voice_client = interaction.guild.voice_client

            for file_name in self.found_files :
                queue_part = {'path': self.downloadPath + file_name, 'author': interaction.user.name}
                self.queue.put(queue_part)

            await interaction.response.send_message("성공적으로 **"+ str(count) +"**개의 노래를 추가했습니다.")

            if self.queue.qsize() == count and not voice_client.is_playing():  # 큐가 비어있으면 재생 시작
                await self.play_next_music(interaction.guild)
        else:
            await interaction.response.send_message("추가할 노래의 개수는 0보다 크고 30보다 작아야 합니다.")

    @app_commands.command(
        name="컨트롤",
        description="미디어 컨트롤러를 표시합니다."
    )
    async def med_controller(self, interaction: Interaction) -> None:
        btnVlUp = Button(label="🔊", style=ButtonStyle.secondary)
        btnVlDown = Button(label="🔉", style=ButtonStyle.secondary)
        btnPlayList = Button(label="🎶", style=ButtonStyle.secondary)
        btnSearch = Button(label="🔍", style=ButtonStyle.secondary)
        btnInsert = Button(label="+", style=ButtonStyle.secondary)
        btnStop = Button(label="⏸️", style=ButtonStyle.primary)
        btnPlay = Button(label="▶️", style=ButtonStyle.primary)
        btnSkip = Button(label="⏭️", style=ButtonStyle.primary)
        btnRes  = Button(label="⏯️", style=ButtonStyle.primary)
        btnRan = Button(label="Ran", style=ButtonStyle.primary)

        async def btn_vl_up_callback(interaction: Interaction):
            member: Member = interaction.user
            voice_channel: VoiceChannel = member.voice.channel
            voice_client = interaction.guild.voice_client

            if voice_client is None or not voice_client.is_connected():
                voice_client = await voice_channel.connect()

            new_volume = self.change_volume(5)
            voice_client.source.volume = new_volume
            voice_client.pause()  # 현재 재생 중인 오디오를 중지하고
            voice_client.resume()  # 새로운 볼륨으로 다시 시작

            await interaction.response.send_message("볼륨을 5 증가시킵니다. 현재 볼륨 : " + str(new_volume * 100), view=view)
            await interaction.message.delete()

        async def btn_vl_down_callback(interaction: Interaction):
            member: Member = interaction.user
            voice_channel: VoiceChannel = member.voice.channel
            voice_client = interaction.guild.voice_client

            if voice_client is None or not voice_client.is_connected():
                voice_client = await voice_channel.connect()

            new_volume = self.change_volume(-5)
            voice_client.source.volume = new_volume
            voice_client.pause()  # 현재 재생 중인 오디오를 중지하고
            voice_client.resume()  # 새로운 볼륨으로 다시 시작

            await interaction.response.send_message("볼륨을 5 감소시킵니다. 현재 볼륨 : " + str(new_volume * 100), view=view)
            await interaction.message.delete()

        async def btn_stop_callback(interaction: Interaction):
            member: Member = interaction.user
            voice_channel: VoiceChannel = member.voice.channel
            voice_client = interaction.guild.voice_client

            if voice_client is None or not voice_client.is_connected():
                voice_client = await voice_channel.connect()

            voice_client.pause()
            await interaction.response.send_message("음악을 정지시킵니다.", view=view)
            await interaction.message.delete()

        async def btn_play_callback(interaction: Interaction):
            member: Member = interaction.user
            voice_channel: VoiceChannel = member.voice.channel
            voice_client = interaction.guild.voice_client

            if voice_client is None or not voice_client.is_connected():
                voice_client = await voice_channel.connect()

            voice_client.resume()
            await interaction.response.send_message("음악을 재생시킵니다.", view=view)
            await interaction.message.delete()

        async def btn_reset_callback(interaction: Interaction):
            member: Member = interaction.user
            voice_channel: VoiceChannel = member.voice.channel
            voice_client = interaction.guild.voice_client

            if voice_client is None or not voice_client.is_connected():
                voice_client = await voice_channel.connect()
            voice_client.pause()
            time.sleep(0.5)
            voice_client.resume()
            await interaction.response.send_message("음악을 중지시키고 다시 재생 시킵니다.", view=view)
            await interaction.message.delete()

        async def btn_skip_callback(interaction: Interaction):
            member: Member = interaction.user
            voice_channel: VoiceChannel = member.voice.channel
            voice_client = interaction.guild.voice_client

            if voice_client is None or not voice_client.is_connected():
                voice_client = await voice_channel.connect()

            if self.queue.qsize() > 0 :
                await self.play_next_music(interaction.guild)
            else :
                if self.isRandomAppend:
                    self.found_files = self.search_random_music(1)
                    for file_name in self.found_files:
                        queue_part = {'path': self.downloadPath + file_name, 'author': '랜덤 추가'}
                        self.queue.put(queue_part)
                        await self.play_next_music(interaction.guild)
                        await interaction.response.send_message("랜덤으로 추가한 다음 노래 **『" + self.now_music_name.split('/')[1] +"』** 을 재생합니다.", view=view)
                await interaction.response.send_message("플레이리스트에 다음 노래가 없습니다.",view=view)

            await interaction.message.delete()

        async def btn_playList_callback(interaction: Interaction):
            table = self.makePlayList()
            await interaction.channel.send(table)
            await interaction.response.send_message("플레이리스트를 출력 했습니다.", view=view)
            await interaction.message.delete()

        async def btn_search_callback(interaction: Interaction):
            try:
                await interaction.response.send_message("어떤곡을 검색하시겠습니까?", view=view)
                await interaction.message.delete()
                response = await self.bot.wait_for("message", check=lambda message: message.author == interaction.user,
                                                   timeout=30)  # 사용자로부터 입력 대기
                self.found_files = self.search_music(response.content)
                if len(self.found_files) != 0:
                    search_results = "\n".join([f"{index}. {filename}" for index, filename in self.found_files])
                    await interaction.followup.send(
                        f"**{response.content}**의 검색 결과:\n{search_results}\n추가버튼을 누르고 추가하고자 하는 번호를 입력해주세요.")
                else:
                    await interaction.followup.send("검색 결과가 없습니다.")

            except asyncio.TimeoutError:
                await interaction.followup.send("입력 시간이 초과되었습니다.")

        async def btn_insert_callback(interaction: Interaction):
            if len(self.found_files) == 0:
                await interaction.response.send_message("먼저 돋보기 버튼을 눌러서 검색을 해주세요", view=view)
                await interaction.message.delete()
            await interaction.response.send_message("어떤 곡을 추가하시겠습니까?", view=view)
            await interaction.message.delete()
            response = await self.bot.wait_for("message", check=lambda message: message.author == interaction.user,
                                               timeout=30)  # 사용자로부터 입력 대기
            num = int(response.content)
            if 1 <= num <= len(self.found_files):
                filename = self.found_files[num - 1][1]
                queue_part = {'path': self.downloadPath + filename, 'author': response.author}
                self.queue.put(queue_part)

                await interaction.followup.send("**" + filename + "** 을 성공적으로 플레이리스트에 추가하였습니다")

                member: Member = interaction.user
                voice_channel: VoiceChannel = member.voice.channel
                voice_client = interaction.guild.voice_client

                if voice_client is None or not voice_client.is_connected():
                    await interaction.response.send_massage("먼저 보이스채널에 접속해주세요")

                if self.queue.qsize() == 1 and not voice_client.is_playing():  # 큐가 비어있으면 재생 시작
                    await self.play_next_music(interaction.guild)

            else:
                await interaction.response.send_message("유효한 번호를 입력해주세요.")

        async def btn_random_play_callback(interaction: Interaction):
            if not self.isRandomAppend:  # 큐가 비어있으면 재생 시작
                self.isRandomAppend = True
                await interaction.response.send_message("이제 노래가 비었을 때 랜덤으로 노래를 재생합니다.", view=view)
            else:
                self.isRandomAppend = False
                await interaction.response.send_message("이제 노래가 비었을 때 랜덤으로 노래를 재생하지 않습니다.", view=view)
            await interaction.message.delete()

        btnVlUp.callback = btn_vl_up_callback
        btnVlDown.callback = btn_vl_down_callback
        btnStop.callback = btn_stop_callback
        btnPlay.callback = btn_play_callback
        btnSkip.callback = btn_skip_callback
        btnPlayList.callback = btn_playList_callback
        btnSearch.callback = btn_search_callback
        btnInsert.callback = btn_insert_callback
        btnRes.callback = btn_reset_callback
        btnRan.callback = btn_random_play_callback
        view = View()

        view.add_item(btnVlDown)
        view.add_item(btnVlUp)
        view.add_item(btnPlayList)
        view.add_item(btnSearch)
        view.add_item(btnInsert)
        view.add_item(btnStop)
        view.add_item(btnPlay)
        view.add_item(btnSkip)
        view.add_item(btnRes)
        view.add_item(btnRan)

        await interaction.response.send_message("버튼을 눌러서 조작해주세요.", view=view)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        music(bot),
        guilds=[]
    )