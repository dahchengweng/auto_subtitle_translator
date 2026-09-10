# YouTube Video/MP3 Downloader & Auto Subtitle Generator

一個基於 Python 的自動化工具，使用 **Singleton 模式** 進行架構設計。能自動從 YouTube 下載最高畫質影片並分離出 MP3 音檔，隨後呼叫本機的 **`faster-whisper`** (支援 Turbo 模型) 進行語音辨識，最終將產生的中/英文字幕以軟字幕形式無損快速封裝回影片中。

## 🌟 功能特點
- **雙料下載**：同一次下載流程中，同時保留最高畫質影片檔與 192kbps MP3 音檔。
- **超速辨識**：採用 `faster-whisper` 架構，辨識速度比 OpenAI 原生 Whisper 快達 4 倍。
- **本機離線載入**：支援直接指定本機的 `large-v3-turbo` 模型路徑，100% 離線執行。
- **無損字幕封裝**：利用 FFmpeg 將 `.srt` 作為軟字幕軌（Soft Subtitle）包入影片，不需重新編碼，1 秒內即可完成合成。
- **互動選單**：支援防呆的命令列互動選單，可自由選擇翻譯成中文或辨識為英文。

## 🛠️ 環境需求與安裝

### 1. 安裝系統工具 FFmpeg
本專案的影片下載、音訊分離與字幕合成皆高度依賴 **FFmpeg**。
- **Windows**: 請下載 FFmpeg 執行檔，並將 `bin` 資料夾路徑加入系統的環境變數 (Path)。
- **Mac**: 透過 Homebrew 安裝：`brew install ffmpeg`

### 2. 安裝 Python 套件
請在終端機中執行以下指令安裝必要函式庫：
```bash
pip install yt-dlp faster-whisper
```
*(備註：若要在 NVIDIA 顯示卡上啟用 GPU 加速，請確保已安裝對應版本的 CUDA 與 cuDNN)*

## 📂 專案檔案結構
```text
├── ytdl_singleton.py          # YouTube 影音下載模組 (Singleton)
├── whisper_singleton.py       # faster-whisper 語音辨識模組 (Singleton)
├── merger_srt_to_video.py     # FFmpeg 字幕合成模組 (Singleton)
├── main.py                    # 主程式進入點 (互動式選單)
├── .gitignore                 # Git 忽略檔案設定
└── README.md                  # 專案說明文件
```

## 🚀 使用說明
1. 打開 `main.py`，將 `my_whisper_path` 變數修改為您電腦中 `large-v3-turbo` 模型解壓後的最深層絕對路徑（包含 `model.bin` 與 `config.json` 的資料夾）。
2. 執行主程式：
   ```bash
   python main.py
   ```
3. 依畫面上提示輸入 YouTube 影片網址。
4. 選擇您要生成的字幕語言 (`1` 為中文，`2` 為英文)。
5. 執行完成後，所有產出的影片、MP3、SRT 檔案皆會儲存於自動建立的 `my_videos/` 資料夾中。

## 📄 授權條款
本專案採用 [MIT License](LICENSE.md) 授權。
