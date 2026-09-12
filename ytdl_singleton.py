import os
import yt_dlp

class YouTubeDownloader:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(YouTubeDownloader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, ffmpeg_path=None, output_dir='downloads', quality='320'):
        if self._initialized:
            return
        self.ffmpeg_path = ffmpeg_path
        self.output_dir = output_dir
        self.quality = quality  
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self._initialized = True

    def download_video_and_mp3(self, url):
        """分別單獨下載音訊(MP3)與影片(MP4)，確保兩個實體檔案絕對存在，徹底防呆"""
        try:
            print(f"[開始下載] 正在處理 YouTube 媒體資源...")
            
            # 1. 取得影片 ID 作為唯一檔名基準
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                video_id = info['id']
            
            video_filename = f"{video_id}.mp4"
            mp3_filename = f"{video_id}.mp3"
            
            # 🎯 步驟一：專門下載最佳音訊並強制轉為 MP3
            print(f"🎵 正在單獨分離並下載高品質 MP3 音檔 (音質: {self.quality}kbps)...")
            ydl_opts_audio = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, video_id),  # 先不寫副檔名，讓後處理器補上 .mp3
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': self.quality,
                }],
            }
            if self.ffmpeg_path:
                ydl_opts_audio['ffmpeg_location'] = self.ffmpeg_path
                
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                ydl.download([url])

            # 🎯 步驟二：專門下載最高畫質影片並封裝為 MP4
            print(f"🎬 正在單獨下載最高畫質 MP4 影片檔...")
            ydl_opts_video = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, f"{video_id}.%(ext)s"),
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }
            if self.ffmpeg_path:
                ydl_opts_video['ffmpeg_location'] = self.ffmpeg_path
                
            with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                ydl.download([url])

            # 檢查檔案是否真的都在硬碟裡，做最後防呆
            full_video_path = os.path.join(self.output_dir, video_filename)
            full_mp3_path = os.path.join(self.output_dir, mp3_filename)
            
            if os.path.exists(full_video_path) and os.path.exists(full_mp3_path):
                return video_filename, mp3_filename
            else:
                print("[錯誤] 偵測到下載檔案缺失，請確認 FFmpeg 是否安裝正確。")
                return None, None
            
        except Exception as e:
            print(f"[發生錯誤] 下載流程失敗: {e}")
            return None, None
