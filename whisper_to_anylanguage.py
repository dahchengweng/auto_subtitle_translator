import os
from faster_whisper import WhisperModel
from translate import Translator as LocalTranslator
from opencc import OpenCC

class WhisperTranslatorAny:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WhisperTranslatorAny, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path_or_name=None, device="auto", compute_type="default"):
        if self._initialized:
            return
            
        final_model_path = r"D:\development\localmodels\faster-whisper-medium"
        
        print(f"[系統初始化] 正在本地載入實體 Medium 模型: {final_model_path}...")
        self.model = WhisperModel(
            final_model_path, 
            device=device, 
            compute_type=compute_type
        )
            
        self.cc = OpenCC('s2twp')  # 簡體轉台灣繁體
        print("[系統初始化] Medium 模型本地載入成功！")
        self._initialized = True

    def _format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

    def transcribe_and_translate_custom(self, audio_path, target_lang='zh-TW', output_dir='downloads'):
        """
        終極穩固路由：支援 韓翻中、日翻中、中翻英、英翻中
        """
        if not os.path.exists(audio_path):
            print(f"[錯誤] 找不到音檔: {audio_path}")
            return None

        print(f"\n[語音辨識] 開始處理音檔: {os.path.basename(audio_path)}")
        
        # 1. 智慧偵測原始語言
        _, info = self.model.transcribe(audio_path, beam_size=5)
        source_lang = info.language.lower()
        print(f"🌐 原始語音自動偵測為: 【 {source_lang} 】 (信心度: {info.language_probability:.2f})")

        is_target_zh = "zh" in target_lang.lower()
        
        # 2. 核心路由精準重構
        if source_lang in ["ja", "ko", "en"] and is_target_zh:
            # 🎯 韓翻中、日翻中、英翻中：一律使用 Whisper 生成英文（日/韓轉成英文），再由本地強效執行英翻中！
            if source_lang in ["ja", "ko"]:
                print(f"💡 偵測為【{source_lang}翻中】，強制啟用 [Whisper中轉英文] ➔ [本地強效英翻中] 黃金路由...")
                segments, _ = self.model.transcribe(audio_path, task='translate', beam_size=5)
            else:
                print("💡 偵測為【英翻中】，啟動 [精準英文解碼] ➔ [本地強效英翻中] 路由...")
                segments, _ = self.model.transcribe(audio_path, language='en', beam_size=5)
                
            translator = LocalTranslator(from_lang="en", to_lang="zh-TW")
            need_translate = True
            need_cc = True
            
        elif source_lang == "zh" and target_lang == "en":
            # 🎯 中翻英：Whisper 原生直出完美英文
            print("💡 偵測為【中翻英】，啟動 [Whisper原生本地直翻英文] 路由...")
            segments, _ = self.model.transcribe(audio_path, task='translate', beam_size=5)
            translator = None
            need_translate = False
            need_cc = False
            
        else:
            # 🎯 備援路由：語言相同或無對應直接直出
            print("💡 啟動 [原音逐字稿] 路由...")
            segments, _ = self.model.transcribe(audio_path, beam_size=5)
            translator = None
            need_translate = False
            need_cc = is_target_zh

        # 3. 修正檔名生成邏輯，確保檔名乾淨好找
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        # 修正：強制讓檔名以你在選單中決定的命名為主，方便 mainAny 尋找
        srt_filename = f"{base_name}_{target_lang}.srt"
        full_srt_path = os.path.join(output_dir, srt_filename)

        with open(full_srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, start=1):
                start_time = self._format_time(segment.start)
                end_time = self._format_time(segment.end)
                text = segment.text.strip()
                
                # 執行無衝突的高精準度英翻中
                if need_translate and translator and text:
                    try:
                        text = translator.translate(text)
                    except Exception:
                        pass
                        
                if need_cc:
                    text = self.cc.convert(text)
                    
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")

        print(f"💾 智慧多語系字幕檔 [{srt_filename}] 生成完成！")
        return srt_filename
