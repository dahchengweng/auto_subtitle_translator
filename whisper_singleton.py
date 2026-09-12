import os
from faster_whisper import WhisperModel
from translate import Translator as LocalTranslator
from opencc import OpenCC

class WhisperTranslator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WhisperTranslator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path_or_name='Systran/faster-whisper-medium', cache_dir=None, device="auto", compute_type="default"):
        if self._initialized:
            return
            
        print(f"[系統初始化] 正在載入標準 Medium 模型: {model_path_or_name}...")
        if cache_dir and os.path.exists(cache_dir):
            self.model = WhisperModel(
                model_path_or_name, device=device, compute_type=compute_type,
                download_root=cache_dir, local_files_only=True     
            )
        else:
            self.model = WhisperModel(model_path_or_name, device=device, compute_type=compute_type)
            
        self.cc = OpenCC('s2twp')  # 簡體轉台灣繁體 (英文翻中文時使用)
        self.en_translator = LocalTranslator(from_lang="en", to_lang="zh-TW") # 外部翻譯 (英文片備援用)
        print("[系統初始化] Medium 模型載入成功！")
        self._initialized = True

    def _format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

    def _write_srt(self, segments, output_path, convert_to_tw=False):
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, start=1):
                start_time = self._format_time(segment.start)
                end_time = self._format_time(segment.end)
                text = segment.text.strip()
                if convert_to_tw:
                    text = self.cc.convert(text)
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

    def transcribe_to_chinese(self, audio_path, output_dir='downloads'):
        """適合【英文影片】➔ 翻譯成【繁體中文字幕】"""
        if not os.path.exists(audio_path):
            return None

        print(f"\n[語音辨識] 開始處理音檔: {os.path.basename(audio_path)}")
        # 先讓大模型用標準英文解碼，取得最精準的英文，再外部翻譯防呆
        segments, info = self.model.transcribe(audio_path, language='en')
        print(f"🌐 原始語音偵測: 【 {info.language} 】")
        print("⏳ 正在跨語言翻譯為繁體中文字幕...")

        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        srt_filename = f"{base_name}_zh.srt"
        full_srt_path = os.path.join(output_dir, srt_filename)

        with open(full_srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, start=1):
                start_time = self._format_time(segment.start)
                end_time = self._format_time(segment.end)
                try:
                    translated = self.en_translator.translate(segment.text)
                    final_text = self.cc.convert(translated)
                except Exception:
                    final_text = segment.text  
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{final_text.strip()}\n\n")

        print(f"💾 繁體中文字幕轉檔完成！")
        return srt_filename

    def transcribe_to_english(self, audio_path, output_dir='downloads'):
        """🎯 核心修改：適合【中文影片】➔ 翻譯成【英文字幕】"""
        if not os.path.exists(audio_path):
            return None

        print(f"\n[語音辨識] 開始處理音檔: {os.path.basename(audio_path)}")
        
        # 🌟 關鍵調整：不指定語系（自動偵測中文）或是指定 language='zh'，並強迫開啟 task='translate'
        # Medium 完整模型只要偵測到中文語音，就會在核心內部將它完美「直翻成英文」吐出來！
        segments, info = self.model.transcribe(audio_path, task='translate')
        print(f"🌐 原始語音偵測: 【 {info.language} 】 (信心度: {info.language_probability:.2f})")
        print("⏳ 正在由 Medium 模型本地原生翻譯為英文字幕...")

        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        srt_filename = f"{base_name}_en.srt"
        full_srt_path = os.path.join(output_dir, srt_filename)
        
        # 寫入檔案（因為輸出是英文，convert_to_tw 設為 False 關閉繁簡轉換）
        self._write_srt(segments, full_srt_path, convert_to_tw=False)
        
        print(f"💾 英文字幕轉檔完成！")
        return srt_filename
