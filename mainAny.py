import os
from ytdl_singleton import YouTubeDownloader
from whisper_to_anylanguage import WhisperTranslatorAny
from merger_srt_to_video import VideoSubtitleMerger


def download_media(output_dir="my_video"):
    downloader = YouTubeDownloader(output_dir=output_dir, quality="320")
    print("=== YouTube 全功能智慧翻譯影音下載器 ===")
    video_url = input("請輸入 YouTube 影片網址: ").strip()
    
    if video_url:
        video_name, mp3_filename = downloader.download_video_and_mp3(video_url)
        if video_name and mp3_filename:
            print("\n----------------------------------------")
            print(f"🎉 媒體下載成功！")
            print(f"🎬 影片檔名: {video_name}")
            print(f"🎵 音訊檔名: {mp3_filename}")
            print("----------------------------------------")
            return video_name, mp3_filename
    print("❌ 下載或轉檔失敗。")
    return None, None


def transcribe_custom_flow(filename, srt_path):
    output_dir = srt_path
    
    # 初始化暴力路徑鎖定的翻譯單例 (Singleton)
    final_model_path = r"D:\development\localmodels\faster-whisper-medium"
    translator = WhisperTranslatorAny()
    
    # 🎯 直覺的四大商業翻譯選單
    print("\n請選擇您影片的翻譯模式：")
    print(" [1] 韓文影片 ➔ 翻譯成【繁體中文】字幕 (韓翻中)")
    print(" [2] 日文影片 ➔ 翻譯成【繁體中文】字幕 (日翻中)")
    print(" [3] 英文影片 ➔ 翻譯成【繁體中文】字幕 (英翻中)")
    print(" [4] 中文影片 ➔ 翻譯成【英文】字幕     (中翻英)")
    
    choice = input("請輸入選項 (1, 2, 3 或 4): ").strip()
    
    # 精準對齊的 ISO 語言代碼與 FFmpeg 字幕軌標籤
    lang_map = {
        "1": {"iso": "zh-TW", "ffmpeg": "chi"},
        "2": {"iso": "zh-TW", "ffmpeg": "chi"},
        "3": {"iso": "zh-TW", "ffmpeg": "chi"},
        "4": {"iso": "en",    "ffmpeg": "eng"}
    }
    
    selected = lang_map.get(choice, lang_map["3"]) # 防呆：預設給最常使用的英翻中
    
    # 呼叫客製化智慧多語系翻譯方法
    srt_filename = translator.transcribe_and_translate_custom(
        audio_path=filename, 
        target_lang=selected["iso"], 
        output_dir=output_dir
    )
    
    if srt_filename:
        return os.path.join(output_dir, srt_filename), selected["ffmpeg"]
    return None, None


def main():
    audio_dir = "my_video"
    video_name, mp3_filename = download_media(audio_dir)
    
    if not video_name or not mp3_filename:
        return

    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_filename = os.path.join(base_dir, audio_dir, mp3_filename)
    video_filename = os.path.join(base_dir, audio_dir, video_name)
    srt_path = os.path.join(base_dir, audio_dir)
    
    # 進行智慧翻譯
    srt_fullname, lang_code = transcribe_custom_flow(filename=audio_filename, srt_path=srt_path)
    if srt_fullname is None:
        print(f"Failed to transcribe the audio {audio_filename}")
        return 

    # 執行硬字幕燒錄 ( subbed_burned.mp4 )
    merger = VideoSubtitleMerger()
    transcibed_video_path = merger.merge_srt(
        video_path=video_filename, 
        srt_path=srt_fullname, 
        output_dir=os.path.join(base_dir, audio_dir), 
        lang_code=lang_code
    )
    
    if transcibed_video_path:
        print("\n========================================")
        print("🎉 全自動硬字幕影片燒錄完美完成！")
        print(f"🎬 最終燒錄影片位置: {os.path.join(audio_dir, transcibed_video_path)}")
        print("========================================")


if __name__ == "__main__":
    main()
