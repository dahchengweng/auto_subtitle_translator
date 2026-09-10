import os
from faster_whisper import WhisperModel

class WhisperTranslator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WhisperTranslator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path_or_name='base', device="auto", compute_type="default"):
        """
        model_path_or_name 可以接受：
        1. 官方版本名稱: 'tiny', 'base', 'small', 'medium', 'large-v3'
        2. 本機 CTranslate2 格式的模型資料夾路徑 (例如: 'D:/models/faster-whisper-base')
        device: "auto", "cuda", "cpu"
        compute_type: 運算精度，GPU 推薦 "float16" 或 "int8_float16"，CPU 推薦 "int8"
        """
        if self._initialized:
            return
            
        print(f"[系統初始化] 正在載入 faster-whisper 模型/路徑: {model_path_or_name}...")
        
        # 初始化模型 (faster-whisper 會自動偵測 GPU/CPU)
        self.model = WhisperModel(
            model_path_or_name, 
            device=device, 
            compute_type=compute_type
        )
        
        print("[系統初始化] faster-whisper 模型載入成功！")
        self._initialized = True

    def _format_time(self, seconds):
        """將秒數轉換為 SRT 的時間格式 (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

    def _write_srt(self, segments, output_path):
        """將 faster-whisper 的 segments 迭代器寫入成 SRT 檔案"""
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, start=1):
                start_time = self._format_time(segment.start)
                end_time = self._format_time(segment.end)
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment.text.strip()}\n\n")

    def transcribe_to_chinese(self, audio_path, output_dir='downloads'):
        """強制翻譯/辨識為中文字幕"""
        if not os.path.exists(audio_path):
            print(f"[錯誤] 找不到音檔: {audio_path}")
            return None

        print(f"\n[語音辨識] 開始處理音檔: {os.path.basename(audio_path)}")
        
        # language='zh' 強制輸出中文
        segments, info = self.model.transcribe(audio_path, language='zh')
        print(f"🌐 偵測到原始語音語言: 【 {info.language} 】(信心度: {info.language_probability:.2f})")
        print("⏳ 正在進行語音轉文字並翻譯為中文 (faster-whisper)...")

        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        srt_filename = f"{base_name}_zh.srt"
        full_srt_path = os.path.join(output_dir, srt_filename)

        # faster-whisper 的 segments 是 generator，在寫入時才會真正觸發計算
        self._write_srt(segments, full_srt_path)

        print(f"💾 中文字幕轉檔完成！")
        return srt_filename

    def transcribe_to_english(self, audio_path, output_dir='downloads'):
        """強制翻譯為英文字幕"""
        if not os.path.exists(audio_path):
            print(f"[錯誤] 找不到音檔: {audio_path}")
            return None

        print(f"\n[語音辨識] 開始處理音檔: {os.path.basename(audio_path)}")
        
        # task='translate' 會自動把任何語言翻譯成英文
        segments, info = self.model.transcribe(audio_path, task='translate')
        print(f"🌐 偵測到原始語音語言: 【 {info.language} 】(信心度: {info.language_probability:.2f})")
        print("⏳ 正在進行語音轉文字並翻譯為英文 (faster-whisper)...")

        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        srt_filename = f"{base_name}_en.srt"
        full_srt_path = os.path.join(output_dir, srt_filename)

        self._write_srt(segments, full_srt_path)

        print(f"💾 英文字幕轉檔完成！")
        return srt_filename
