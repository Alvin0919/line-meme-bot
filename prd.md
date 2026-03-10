# LINE Bot 梗圖機器人 - PRD

## 概述
建立一個 LINE 聊天機器人，使用者可透過關鍵字搜尋、編號取圖（t+數字）、隨機抽圖（「抽」）快速獲得主題梗圖。

## 技術約束
- Python Flask + line-bot-sdk v3
- JSON 檔存梗圖資料（< 100 張）
- 圖片儲存：GitHub Raw（之後可切換 Cloudinary/S3）
- 部署平台：Koyeb
- Credentials 透過環境變數管理

## 任務清單
| # | 任務 | 驗收標準（機器可驗證） | passes |
|---|------|----------------------|--------|
| 1 | 建立專案結構（app.py、memes.json、requirements.txt、.gitignore、.env.example、Procfile） | `ls app.py memes.json requirements.txt .gitignore .env.example Procfile` 全部存在 | true |
| 2 | 實作 Flask webhook endpoint + LINE signature 驗證 | `python -m py_compile app.py` 通過 | true |
| 3 | 實作功能 1：關鍵字搜尋（比對 description/tags，回傳最多 20 筆文字結果） | 模擬測試：輸入關鍵字回傳正確格式 `【T0001】描述` | true |
| 4 | 實作功能 2：編號取圖（正則 `^[tT](\d+)$`，回傳 ImageSendMessage） | 模擬測試：`t1` 回傳圖片、`t9999` 回傳超出範圍提示 | true |
| 5 | 實作功能 3：隨機抽圖（輸入「抽」，隨機回傳一張圖） | 模擬測試：輸入「抽」回傳 ImageSendMessage | true |
| 6 | 建立範例 memes.json（5 筆 placeholder 資料）+ 圖片目錄 `images/` | `python -c "import json; d=json.load(open('memes.json','r',encoding='utf-8')); assert len(d)>=5"` 通過 | true |
| 7 | Git 初始化 + credentials 安全檢查 | `git status` 成功 且 `grep -r "sk-\|Bearer\|token.*=.*['\"]" app.py` 無結果 且 `.gitignore` 包含 `.env` | true |

## 優先順序
任務 1（專案結構）→ 2（webhook 骨架）→ 3-5（三大功能）→ 6（範例資料）→ 7（Git + 資安）

## 回饋迴路（每次 commit 前必須通過）
- [ ] `python -m py_compile app.py`（語法檢查）
- [ ] `pip install -r requirements.txt`（依賴安裝）
- [ ] `grep -r "sk-\|Bearer\|token.*=.*['\"]" app.py`（credentials 洩漏檢查）

## 資安規範
- **Credentials 管理**：`LINE_CHANNEL_ACCESS_TOKEN` 和 `LINE_CHANNEL_SECRET` 透過環境變數讀取
- **Webhook 驗證**：使用 line-bot-sdk 內建 X-Line-Signature HMAC-SHA256 驗證
- **使用者輸入**：正則比對 + 搜尋結果限制 20 筆
- **.gitignore 排除**：`.env`、`__pycache__/`、`*.pyc`、`.venv/`

## 逃生計畫
卡住超過 3 次：記錄 BLOCKERS.md → 列已嘗試方案 → 跳到下一個任務
