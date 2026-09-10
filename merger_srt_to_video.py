import os
import subprocess

class VideoSubtitleMerger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(VideoSubtitleMerger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, ffmpeg_path="ffmpeg"):
        """
        ffmpeg_path: 如果系統變數有，用預設 "ffmpeg" 即可。
        否則可以傳入絕對路徑，例如 "C:/ffmpeg/bin/ffmpeg.exe"
        """
        if self._initialized:
            return
        self.ffmpeg_path = ffmpeg_path
        self._initialized = True

    def merge_srt(self, video_path, srt_path, output_dir='my_video', lang_code='chi'):
        """
        將 srt 字幕以軟字幕（Soft Subtitle）形式合成進影片中。
        lang_code: 'chi' 代表中文標籤，'eng' 代表英文標籤。
        """
        if not os.path.exists(video_path) or not os.path.exists(srt_path):
            print("[錯誤] 找不到影片或字幕檔案，無法進行合成。")
            return None

        base_name = os.path.splitext(os.path.basename(video_path))[0]
        ext = os.path.splitext(video_path)[1]
        
        # 為了避免覆蓋原始檔案，輸出檔名加上 _subbed 字樣
        output_filename = f"{base_name}_subbed{ext}"
        output_path = os.path.join(output_dir, output_filename)

        print(f"\n[🎬 字幕合成] 正在封裝字幕至影片: {output_filename}...")

        # FFmpeg 指令：-c copy 代表影音軌直接複製不重新編碼（速度極快）
        # -c:s mov_text (mp4 用) 或 srt (mkv 用)，這裡會根據副檔名自適應處理，最安全是用 copy 或 指定字幕格式
        # 對於 mp4 容器，軟字幕使用 mov_text 格式
        sub_codec = "mov_text" if ext.lower() == ".mp4" else "srt"

        command = [
            self.ffmpeg_path,
            "-y",                # 若檔案存在直接覆蓋
            "-i", video_path,    # 輸入影片
            "-i", srt_path,      # 輸入字幕
            "-c", "copy",        # 複製影音串流（不重新編碼）
            f"-c:s", sub_codec,  # 設定字幕編碼器
            f"-metadata:s:s:0", f"language={lang_code}", # 設定字幕語言標籤
            f"-metadata:s:s:0", f"title={lang_code.upper()} Subtitles",
            output_path
        ]

        try:
            # 執行 FFmpeg (隱藏跳出視窗)
            startupinfo = None
            if os.name == 'nt': # Windows 防呆，避免彈出 CMD 視窗
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, text=True)
            
            if result.returncode == 0:
                print(f"💾 合成影片成功！新影片已儲存。")
                return output_filename
            else:
                print(f"[FFmpeg 錯誤] 合成失敗:\n{result.stderr}")
                return None
        except Exception as e:
            print(f"[發生錯誤] 合成過程出錯: {e}")
            return None
