# Telegram 朋友圈備份機器人

## 專案概覽

本專案提供一個 Telegram 機器人，可以接收使用者轉發的文字和圖片訊息，並自動將這些內容儲存到指定的 Google Drive 資料夾中。此外，機器人還會每天定時生成一份彙總報告。

## 功能

- 接收並儲存文字訊息到 Google Drive
- 接收並儲存圖片到 Google Drive
- 每日自動生成彙總報告
- 可輕鬆部署於 Zeabur 平台

## 事前準備

在部署之前，請先完成以下準備工作：

1.  **取得 Telegram Bot Token**
    - 在 Telegram 中搜尋 `@BotFather`。
    - 輸入 `/newbot` 指令，並按照提示建立一個新的機器人。
    - 記下 BotFather 回傳的 Token，格式類似 `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`。

2.  **取得 Google Service Account 金鑰**
    - 前往 [Google Cloud Console](https://console.cloud.google.com/)。
    - 建立一個新的專案，或選取現有專案。
    - 在左側選單中，前往「APIs & Services」>「Enabled APIs & services」。
    - 點擊「+ ENABLE APIS AND SERVICES」，搜尋並啟用「Google Drive API」。
    - 前往「APIs & Services」>「Credentials」。
    - 點擊「+ CREATE CREDENTIALS」，選擇「Service account」。
    - 填寫 Service account 的名稱，然後點擊「CREATE AND CONTINUE」。
    - 在「Grant this service account access to project」步驟中，選擇「Owner」角色，然後點擊「CONTINUE」。
    - 點擊「DONE」。
    - 在 Credentials 頁面，找到您剛剛建立的 Service account，點擊進入。
    - 前往「KEYS」分頁，點擊「ADD KEY」>「Create new key」。
    - 選擇「JSON」格式，然後點擊「CREATE」。瀏覽器會自動下載一個 JSON 檔案，請妥善保管。

3.  **取得 Google Drive 資料夾 ID**
    - 在您的 Google Drive 中，建立一個新的資料夾，用來存放備份的內容。
    - 打開這個資料夾，複製瀏覽器網址列中的資料夾 ID。網址格式為 `https://drive.google.com/drive/folders/{FOLDER_ID}`。

4.  **分享資料夾權限**
    - 在 Google Drive 中，右鍵點擊您建立的資料夾，選擇「Share」。
    - 將您在步驟 2 中建立的 Service account 的電子郵件地址（可以在 JSON 金鑰檔案中找到 `client_email` 欄位）加入到分享對象中，並給予「Editor」權限。

## 部署到 Zeabur

1.  **Fork 本專案**
    - 將本專案 Fork 到您自己的 GitHub 帳號下。

2.  **在 Zeabur 上建立新專案**
    - 登入 [Zeabur](https://zeabur.com/)。
    - 建立一個新專案，並選擇從 GitHub 匯入。
    - 選擇您剛剛 Fork 的專案。

3.  **設定環境變數**
    - 在 Zeabur 專案的「Variables」分頁中，新增以下環境變數：
      - `TELEGRAM_BOT_TOKEN`: 您在事前準備步驟 1 中取得的 Telegram Bot Token。
      - `GOOGLE_DRIVE_FOLDER_ID`: 您在事前準備步驟 3 中取得的 Google Drive 資料夾 ID。
      - `GOOGLE_SERVICE_ACCOUNT_JSON`: 將您在事前準備步驟 2 中下載的 JSON 金鑰檔案的**內容**複製並貼上到此處。

4.  **部署**
    - Zeabur 會自動偵測到專案中的 Dockerfile 並進行部署。

## 設定 Webhook

部署完成後，Zeabur 會提供一個公開的網址。請將此網址與您的 Telegram Bot 進行綁定：

1.  複製 Zeabur 提供的服務網址，例如 `https://your-service-name.zeabur.app`。
2.  在瀏覽器中開啟以下網址，將 `{YOUR_BOT_TOKEN}` 和 `{YOUR_WEBHOOK_URL}` 替換為您的資訊：
    ```
    https://api.telegram.org/bot{YOUR_BOT_TOKEN}/setWebhook?url={YOUR_WEBHOOK_URL}/{YOUR_BOT_TOKEN}
    ```
    例如：
    ```
    https://api.telegram.org/bot123456:ABC-DEF/setWebhook?url=https://your-service-name.zeabur.app/123456:ABC-DEF
    ```
3.  開啟後，如果看到 `{"ok":true,"result":true,"description":"Webhook was set"}` 的訊息，代表設定成功。

## 每日報告排程

您可以使用 Zeabur 的 Cron Job 功能來定時觸發每日報告的生成。

1.  在 Zeabur 專案中，新增一個 Cron Job 服務。
2.  設定 Cron 表達式為 `0 0 * * *` (每天午夜執行)。
3.  設定要執行的指令，觸發生成報告的腳本。由於我們的應用程式是長時間運行的服務，您可以建立一個簡單的 curl 指令來觸發報告生成。

    *注意：目前的程式碼架構中，每日報告是透過 `print` 輸出，在 Zeabur 環境下需要調整為可被外部觸發的 HTTP 端點。這部分需要進一步開發。*

現在，您的 Telegram 機器人已經準備就緒！您可以開始將朋友圈的內容轉發給它了。
