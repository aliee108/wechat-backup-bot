# Telegram 朋友圈備份機器人 (v3.0)

## 專案概覽

本專案提供一個 Telegram 機器人，可以接收使用者轉發的文字、圖片和影片訊息。當使用者輸入 `/save` 指令時，機器人會將之前轉發的所有內容自動儲存到指定的 Google Drive 資料夾中，並實現自動分類和自定義資料夾名稱。

## 新功能 (v3.0)

- **自定義資料夾名稱**: 使用 `/setfolder` 指令選擇預設資料夾名稱，或直接輸入自定義名稱。
- **指令觸發備份**: 使用 `/save` 指令來觸發備份，方便一次性處理多個媒體檔案。
- **自動資料夾分類**: 檔案會自動儲存在 `/{根目錄}/{自定義名稱}/{年-月-日}/message_{訊息ID}/` 的結構中。
- **影片支援**: 新增支援 MP4 和 MOV 格式的影片上傳 (單檔最大 50MB)。
- **每日彙總報告**: 每天午夜自動生成前一天的備份內容彙總報告，並儲存在對應日期的資料夾中。

## 使用流程

1.  對機器人發送 `/start` 開始互動。
2.  輸入 `/setfolder` 指令，選擇一個預設資料夾名稱，或直接輸入您想要的名稱。
3.  轉發您想要備份的朋友圈文字、圖片或影片給機器人。
4.  可以多次轉發，機器人會暫時記錄所有內容。
5.  當您轉發完一篇貼文的所有內容後，輸入 `/save` 指令。
6.  機器人會將所有暫存的內容上傳到 Google Drive，並按自定義名稱、日期和訊息 ID 建立資料夾存放。

## 事前準備

部署前，請確保您已完成以下準備工作 (與舊版相同)：

1.  **取得 Telegram Bot Token** (透過 `@BotFather`)。
2.  **取得 Google Service Account 金鑰** (在 Google Cloud Console 中建立並啟用 Drive API)。
3.  **取得 Google Drive 根資料夾 ID**。
4.  **分享資料夾權限**給您的 Service Account 電子郵件。

## 部署到 Zeabur

部署流程與先前版本基本相同：

1.  **Fork 本專案**到您的 GitHub 帳號。
2.  **在 Zeabur 上建立新專案**並從 GitHub 匯入您的倉庫。
3.  **設定環境變數**:
    - `TELEGRAM_BOT_TOKEN`
    - `GOOGLE_DRIVE_FOLDER_ID`
    - `GOOGLE_SERVICE_ACCOUNT_JSON`
4.  **設定根目錄 (Root Directory)**: 在服務的 "Settings" 中，確保根目錄為 `/` 或留空。
5.  **部署**並等待完成。

## 設定 Webhook

部署完成後，使用 Zeabur 提供的**公開網域** (`.zeabur.app` 結尾) 設定 Webhook：

```
https://api.telegram.org/bot{YOUR_BOT_TOKEN}/setWebhook?url={YOUR_WEBHOOK_URL}/{YOUR_BOT_TOKEN}
```

看到 `{"ok":true,"result":true,"description":"Webhook was set"}` 即表示成功。

現在，您的升級版機器人已準備就緒！
