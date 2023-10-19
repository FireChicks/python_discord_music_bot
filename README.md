# python_discord_music_bot
파이썬 디스코드 뮤직 봇입니다.

큐를 활용한 플레이리스트 생성 기능과 재생, 중지, 다음 노래 재생, 볼륨조절 기능및 플레이리스트 확인등이 들어가있습니다.
target_channel_id의 채널에서 입력받은 유튜브 링크를 파싱해서 yt_dlp를 이용해 노래를 다운받고 입력받은 순서대로 ffmpeg 포맷을 사용해 재생해줍니다.

다운받은 노래들 리스트들을 검색해서 추가하는 기능도 들어있습니다.<br>
<br>
<hr>
<br>
<h3>노래 추가</h3>
<img src="https://drive.google.com/uc?export=view&id=1OeY_yyt-LRBgGx9AX0YnKBBXA5TNBo-3">
<br>target_channel_id의 채널에서 유튜브 링크를 올리면 이런식으로 자동으로 노래에 다운 후 추가가 완료됩니다.
(이미 이전에 다운로드된적 있는 파일이면 바로 플레이리스트에 추가)<br>
<br>
<hr>
<br>
<h3>컨트롤 패널</h3>
<img src="https://drive.google.com/uc?export=view&id=15JFya1TAZ6CBJnKSGz8aa67WCjrybEw9">
<br>/컨트롤 명령어 입력시 다음과 같은 컨트롤 창이 표시가 됩니다. 간단한 조작이 가능합니다.
플레이리스트 버튼 클릭시 다음과 같은 플레이리스트가 출력이 됩니다.<br>
<img src="https://drive.google.com/uc?export=view&id=1z_GzSkQibIB8r9QGO0xawLVJCeolJ40j">
<br>
<hr>
<br>
<h3>노래 검색</h3>
<img src="https://drive.google.com/uc?export=view&id=1v7QAZnthBx1kDf9ogIB22kx7GLSMB_55">
<br>이미 다운로드 받은 노래명을 사용해 검색할수도 있습니다. 입력한 문자열을 사용해서 검색해줍니다.<br>
<img src="https://drive.google.com/uc?export=view&id=19F7v7BhFaDMVUrl-PoPo2dAF90LB8miF)https://drive.google.com/uc?export=view&id=19F7v7BhFaDMVUrl-PoPo2dAF90LB8miF">
<br>검색한 내용은 다음과 같이 버튼으로 표시되며 버튼을 클릭하면 자동으로 노래가 플레이리스트큐에 추가됩니다.<br>
