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
        if self._initialized:
            return
        self.ffmpeg_path = ffmpeg_path
        self._initialized = True

    def merge_srt(self, video_path, srt_path, output_dir='downloads', lang_code='chi'):
        """將 srt 字幕作為『硬字幕 (Hard Subtitles)』直接燒錄固定在影片畫面上"""
        if not os.path.exists(video_path) or not os.path.exists(srt_path):
            print("[錯誤] 找不到影片或字幕檔案，無法進行合成。")
            return None

        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_filename = f"{base_name}_burned.mp4"
        output_path = os.path.join(output_dir, output_filename)

        print(f"\n[🎬 字幕燒錄] 正在將字幕直接燒死至影片畫面: {output_filename}...")
        print("💡 提示：硬字幕需要重新渲染影片影像，會消耗一些 CPU 資源，請稍候...")

        # 🎯 核心修正 1：FFmpeg 的 subtitles 濾鏡在 Windows 下對冒號與反斜線有極嚴格的格式要求
        # 必須將 D:\path\file.srt 轉換為 D\\:/path/file.srt 格式，否則 FFmpeg 會報路徑解析錯誤
        safe_srt_path = srt_path.replace("\\", "/").replace(":", "\\:")

        # 🎯 核心修正 2：明確指定中文字型 (Windows 內建的微軟正黑體)，並設定字體大小與樣式
        # 這樣可以徹底避免 Windows 上燒錄中文字幕出現亂碼或方塊字的問題
        video_filter = f"subtitles='{safe_srt_path}':force_style='Fontname=Microsoft JhengHei,Fontsize=18,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=1,Outline=2'"

        command = [
            self.ffmpeg_path,
            "-y",                        # 若檔案存在直接覆蓋
            "-i", video_path,            # 輸入影片
            "-vf", video_filter,         # 載入精心設計的硬字幕影像濾鏡
            "-c:v", "libx264",           # 轉換為標準且相容性最高的 H.264 影片編碼
            "-preset", "fast",           # 渲染速度設定
            "-crf", "22",                # 保持極佳畫質不失真 (22 為高品質平衡點)
            "-c:a", "copy",              # 聲音軌直接複製，不浪費時間重新編碼
            output_path
        ]

        try:
            startupinfo = None
            if os.name == 'nt': 
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
            result = subprocess.run(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                startupinfo=startupinfo, 
                encoding="utf-8",
                errors="ignore"
            )
            
            if result.returncode == 0:
                print(f"💾 字幕影片燒錄成功！新影片已儲存。")
                return output_filename
            else:
                print(f"[FFmpeg 錯誤] 燒錄失敗:\n{result.stderr}")
                return None
        except Exception as e:
            print(f"[發生錯誤] 燒錄過程出錯: {e}")
            return None
