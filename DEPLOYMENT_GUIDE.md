# Telegram 朋友圈備份機器人 - 完整部署指南

## 系統架構概覽

本系統由以下主要元件組成：

| 元件 | 功能 | 技術棧 |
|------|------|--------|
| Telegram Bot | 接收使用者訊息和圖片 | Python + FastAPI |
| Google Drive API | 儲存文字和圖片 | Google API Client |
| Zeabur | 雲端部署和託管 | Docker + 環境變數 |
| 排程器 | 每日報告生成 | APScheduler (可選) |

## 第一步：準備 Telegram Bot

### 1.1 建立 Telegram Bot

1. 打開 Telegram 應用程式，搜尋 `@BotFather`。
2. 點擊「START」開始對話。
3. 輸入 `/newbot` 指令。
4. BotFather 會要求您輸入機器人名稱，例如 `My WeChat Backup Bot`。
5. 接著要求輸入使用者名稱（必須以 `bot` 結尾），例如 `my_wechat_backup_bot`。
6. BotFather 會回傳一個 Token，格式如下：

```
123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

**請妥善保管此 Token，稍後會用到。**

### 1.2 測試 Bot 是否可用

在 Telegram 中搜尋您剛建立的機器人使用者名稱，點擊「START」按鈕。如果機器人回應了歡迎訊息，代表 Bot 已正常運作。

## 第二步：設定 Google Drive 存取權限

### 2.1 建立 Google Cloud 專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)。
2. 點擊頁面頂部的「Select a Project」下拉選單。
3. 點擊「NEW PROJECT」。
4. 輸入專案名稱，例如 `WeChat Backup Bot`。
5. 點擊「CREATE」。

### 2.2 啟用 Google Drive API

1. 在 Google Cloud Console 中，確保您已選擇剛建立的專案。
2. 在左側導覽選單中，點擊「APIs & Services」>「Library」。
3. 搜尋「Google Drive API」。
4. 點擊搜尋結果中的「Google Drive API」。
5. 點擊「ENABLE」按鈕。

### 2.3 建立 Service Account

1. 在 Google Cloud Console 中，點擊「APIs & Services」>「Credentials」。
2. 點擊「+ CREATE CREDENTIALS」按鈕。
3. 在下拉選單中選擇「Service Account」。
4. 填寫以下資訊：
   - **Service account name**: 例如 `wechat-backup-bot`
   - **Service account ID**: 系統會自動產生
   - **Description**: 例如 `Service account for WeChat backup bot`
5. 點擊「CREATE AND CONTINUE」。
6. 在「Grant this service account access to project」步驟中：
   - 點擊「Select a role」下拉選單。
   - 搜尋並選擇「Editor」角色。
   - 點擊「CONTINUE」。
7. 點擊「DONE」完成建立。

### 2.4 建立並下載服務帳戶金鑰

1. 在 Credentials 頁面中，找到您剛建立的 Service Account，點擊進入。
2. 點擊「KEYS」分頁。
3. 點擊「ADD KEY」>「Create new key」。
4. 在彈出的對話框中，選擇「JSON」格式。
5. 點擊「CREATE」。
6. 瀏覽器會自動下載一個 JSON 檔案，請將其保存到安全的位置。

**此 JSON 檔案包含敏感資訊，請勿洩露。**

### 2.5 建立 Google Drive 資料夾

1. 打開 [Google Drive](https://drive.google.com/)。
2. 點擊「+ New」>「Folder」。
3. 輸入資料夾名稱，例如 `WeChat Backup`。
4. 點擊「CREATE」。
5. 打開新建立的資料夾。
6. 從瀏覽器網址列複製資料夾 ID。網址格式為 `https://drive.google.com/drive/folders/{FOLDER_ID}`。

**記下此資料夾 ID，稍後會用到。**

### 2.6 授予 Service Account 存取權限

1. 在 Google Drive 中，右鍵點擊您建立的資料夾。
2. 選擇「Share」。
3. 打開您下載的 JSON 金鑰檔案，找到 `client_email` 欄位。
4. 將此電子郵件地址複製到 Google Drive 的分享對話框中。
5. 確保權限設為「Editor」。
6. 點擊「Share」。

## 第三步：部署到 Zeabur

### 3.1 準備 GitHub 倉庫

1. 登入您的 GitHub 帳號。
2. 建立一個新的倉庫，例如 `wechat-backup-bot`。
3. 將本專案的所有檔案推送到此倉庫。

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/wechat-backup-bot.git
git push -u origin main
```

### 3.2 在 Zeabur 上建立服務

1. 登入 [Zeabur](https://zeabur.com/)。
2. 點擊「Create Project」。
3. 選擇「Deploy from GitHub」。
4. 授權 Zeabur 訪問您的 GitHub 帳號。
5. 選擇您剛建立的倉庫 `wechat-backup-bot`。
6. 點擊「Deploy」。

### 3.3 設定環境變數

1. 在 Zeabur 專案頁面中，點擊您的服務。
2. 前往「Variables」分頁。
3. 新增以下環境變數：

| 變數名稱 | 值 | 說明 |
|---------|-----|------|
| `TELEGRAM_BOT_TOKEN` | `123456:ABC-DEF...` | 您在第一步中取得的 Telegram Bot Token |
| `GOOGLE_DRIVE_FOLDER_ID` | `1a2b3c4d5e6f7g8h9i0j` | 您在第二步中取得的 Google Drive 資料夾 ID |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | `{...完整的 JSON 內容...}` | 您在第二步中下載的 JSON 金鑰檔案的完整內容 |
| `PORT` | `8080` | 應用程式監聽的埠號 |

**設定 `GOOGLE_SERVICE_ACCOUNT_JSON` 時，請將整個 JSON 檔案的內容複製並貼上。**

### 3.4 取得 Zeabur 服務網址

1. 在 Zeabur 專案頁面中，找到您的服務。
2. 在「Domains」分頁中，您會看到一個自動分配的網址，例如 `https://wechat-backup-bot-abc123.zeabur.app`。

**記下此網址，稍後會用到。**

## 第四步：設定 Telegram Webhook

Webhook 是 Telegram 用來通知您的應用程式有新訊息的機制。

1. 在瀏覽器中打開以下網址（將佔位符替換為您的實際值）：

```
https://api.telegram.org/bot{YOUR_BOT_TOKEN}/setWebhook?url={YOUR_ZEABUR_URL}/{YOUR_BOT_TOKEN}
```

例如：

```
https://api.telegram.org/bot123456:ABC-DEF/setWebhook?url=https://wechat-backup-bot-abc123.zeabur.app/123456:ABC-DEF
```

2. 打開此網址後，瀏覽器應該顯示以下訊息：

```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

**如果看到此訊息，代表 Webhook 設定成功。**

## 第五步：測試機器人

1. 在 Telegram 中打開您的機器人。
2. 發送 `/start` 指令。
3. 機器人應該回應歡迎訊息。
4. 嘗試發送一條文字訊息，例如「Hello」。
5. 機器人應該回應訊息已儲存的確認。
6. 檢查您的 Google Drive 資料夾，應該能看到新建立的文字檔案。
7. 嘗試發送一張圖片。
8. 機器人應該回應圖片已儲存的確認。
9. 檢查 Google Drive 資料夾，應該能看到新上傳的圖片。

## 常見問題

### 問題 1：機器人無法接收訊息

**可能原因**：
- Webhook 未正確設定。
- Zeabur 服務未正常運行。
- 環境變數未正確設定。

**解決方案**：
1. 檢查 Zeabur 服務的日誌，查看是否有錯誤訊息。
2. 重新設定 Webhook，確保網址正確。
3. 檢查所有環境變數是否正確設定。

### 問題 2：無法上傳到 Google Drive

**可能原因**：
- Service Account 沒有存取資料夾的權限。
- Google Service Account JSON 金鑰不正確。
- Google Drive API 未啟用。

**解決方案**：
1. 確保 Service Account 已被添加到 Google Drive 資料夾的分享清單中，且權限為「Editor」。
2. 重新檢查 JSON 金鑰檔案的內容是否正確。
3. 在 Google Cloud Console 中確認 Google Drive API 已啟用。

### 問題 3：每日報告未生成

**可能原因**：
- 排程器未正確配置。
- Zeabur 服務已停止運行。

**解決方案**：
1. 檢查 Zeabur 服務是否正在運行。
2. 查看服務日誌，確認排程器是否在執行。

## 後續改進建議

1. **增加更多訊息類型支援**：目前只支援文字和圖片，可以擴展為支援視頻、音頻等。
2. **實現更智能的分類**：根據訊息內容自動分類到不同的 Google Drive 資料夾。
3. **新增搜尋功能**：讓使用者可以搜尋已備份的內容。
4. **實現備份恢復**：允許使用者恢復已刪除的備份。
5. **多使用者支援**：支援多個使用者同時使用同一個機器人。

## 技術支援

如果遇到問題，請檢查以下資源：

- [Telegram Bot API 文件](https://core.telegram.org/bots/api)
- [Google Drive API 文件](https://developers.google.com/drive/api)
- [Zeabur 文件](https://zeabur.com/docs)

祝您使用愉快！
