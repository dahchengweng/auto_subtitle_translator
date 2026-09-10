import os
import yt_dlp

class YouTubeDownloader:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(YouTubeDownloader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, ffmpeg_path=None, output_dir='my_video'):
        if self._initialized:
            return
            
        self.ffmpeg_path = ffmpeg_path
        self.output_dir = output_dir
        self.last_video_file = None  # 儲存最終的影片檔名
        self.last_mp3_file = None    # 儲存最終的 MP3 檔名
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        self._initialized = True

    def _ytdl_hook(self, d):
        """用來攔截下載與合併完成後的實體檔案"""
        if d['status'] == 'finished':
            # 這裡能抓到下載過程中產生或最終合併的檔案路徑
            filepath = d['info_dict'].get('filepath')
            if filepath:
                filename = os.path.basename(filepath)
                # 依副檔名判斷並存入對應的變數
                if filename.lower().endswith('.mp3'):
                    self.last_mp3_file = filename
                else:
                    self.last_video_file = filename

    def download_video_and_mp3(self, url):
        """下載最高畫質影片，並同時額外轉出一份 MP3，成功會回傳 (影片檔名, MP3檔名)"""
        self.last_video_file = None
        self.last_mp3_file = None
        
        outtmpl_path = os.path.join(self.output_dir, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best', 
            'outtmpl': outtmpl_path,
            'quiet': True,
            # 核心設定：抽取音訊成 MP3，並開啟 keepvideo 確保原本的影片不會被刪除
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4', # 確保影片格式統一為方便合成的 mp4
                }
            ],
            'keepvideo': True, # 🌟 關鍵：強制保留下載下來的影片檔
        }

        if self.ffmpeg_path:
            ydl_opts['ffmpeg_location'] = self.ffmpeg_path

        # 透過 postprocessor_hooks 追蹤最終產生的所有檔案
        ydl_opts['postprocessor_hooks'] = [self._ytdl_hook]

        try:
            print(f"[開始下載] 正在下載影片並分離 MP3 音檔...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 這裡 yt-dlp 會自動處理：下載影音 -> 複製一份轉 MP3 -> 保留原影音
                info = ydl.extract_info(url, download=True)
                
                # 防呆補充：如果 hook 沒抓完整，從 info 內補抓標題檔名
                if not self.last_video_file:
                    self.last_video_file = f"{info['title']}.mp4"
                if not self.last_mp3_file:
                    self.last_mp3_file = f"{info['title']}.mp3"
                    
            return self.last_video_file, self.last_mp3_file
        except Exception as e:
            print(f"[發生錯誤] 下載失敗: {e}")
            return None, None
