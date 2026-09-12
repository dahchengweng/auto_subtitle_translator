import os
from ytdl_singleton import YouTubeDownloader
from whisper_singleton import WhisperTranslator
from merger_srt_to_video import VideoSubtitleMerger


def download_media(output_dir="my_video"):
    # 使用傳入的 output_dir，並統一設定音質
    downloader = YouTubeDownloader(output_dir=output_dir)
    
    print("=== YouTube 影音下載器 ===")
    video_url = input("請輸入 YouTube 影片網址: ").strip()
    
    if video_url:
        # 🎯 修改點：呼叫同時下載影片與 MP3 的方法，接收兩個回傳檔名
        video_name, mp3_filename = downloader.download_video_and_mp3(video_url)
        
        if video_name and mp3_filename:
            print("\n----------------------------------------")
            print(f"🎉 下載成功！")
            print(f"📂 儲存資料夾: {downloader.output_dir}")
            print(f"🎬 影片檔名: {video_name}")
            print(f"🎵 音訊檔名: {mp3_filename}")
            print("----------------------------------------")
            return video_name, mp3_filename
        else:
            print("❌ 下載或轉檔失敗。")
            return None, None
    else:
        print("錯誤：網址不能為空！")
        return None, None


def transcribe(filename, srt_path):
    if not os.path.exists(filename):
        print(f"{filename} does not exist.")
        return None, None
        
    output_dir = srt_path
    model_path = r"D:\development\localmodels\models--mobiuslabsgmbh--faster-whisper-large-v3-turbo\snapshots\0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf"
    translator = WhisperTranslator(model_path_or_name=model_path)
    
    print("\n請選擇要產生的字幕語言：")
    print(" [1] 翻譯成中文 (Chinese)")
    print(" [2] 辨識為英文 (English) ※註：適合原始為英文的影片")
    lang_choice = input("請輸入選項(1或2): ").strip()
    
    if lang_choice not in ["1", "2"]:
        print("⚠️ 無效的選項，系統離開")
        return None, None
        
    srt_filename = None
    if lang_choice == "1":
        srt_filename = translator.transcribe_to_chinese(audio_path=filename, output_dir=output_dir)
        lang_code = "chi"
    else:
        srt_filename = translator.transcribe_to_english(audio_path=filename, output_dir=output_dir)
        lang_code = "eng"
        
    if srt_filename:
        print("\n========================================")
        print("🎉 語音辨識順利完成！")
        print(f"🎵 音檔位置: {filename}")
        print(f"📝 字幕位置: {os.path.join(output_dir, srt_filename)}")
        print("========================================")
        return os.path.join(output_dir, srt_filename), lang_code
    else:
        print("❌ 字幕翻譯失敗。")
        return None, None


def main():
    audio_dir = "my_video"
    
    # 🎯 修正點：download_media 現在會正確回傳影片與音檔名稱
    video_name, mp3_filename = download_media(audio_dir)
    
    if not video_name or not mp3_filename:
        print("Failed to download media files.")
        return

    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_filename = os.path.join(base_dir, audio_dir, mp3_filename)
    video_filename = os.path.join(base_dir, audio_dir, video_name)
    srt_path = os.path.join(base_dir, audio_dir)
    
    # 進行翻譯
    srt_fullname, lang_code = transcribe(filename=audio_filename, srt_path=srt_path)
    if srt_fullname is None:
        print(f"Failed to transcribe the audio {audio_filename}")
        return 
        
    print(f"\n{audio_filename} has succeed to be transcribed to {srt_fullname}")

    # 合成字幕
    merger = VideoSubtitleMerger()
    transcibed_video_path = merger.merge_srt(
        video_path=video_filename, 
        srt_path=srt_fullname, 
        output_dir=os.path.join(base_dir, audio_dir), # 使用絕對路徑確保 FFmpeg 輸出位置正確
        lang_code=lang_code
    )
    
    if transcibed_video_path:
        print("\n========================================")
        print("🎉 所有製程完美完成！")
        print(f"🎬 最終內嵌字幕影片: {os.path.join(audio_dir, transcibed_video_path)}")
        print("💡 提示: 播放此影片時，請在播放器中開啟「字幕軌」即可看到字幕！")
        print("========================================")
    else:
        print("❌ 字幕與影片合成失敗。")


if __name__ == "__main__":
    main()
