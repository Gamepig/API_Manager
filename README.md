# PM2 API Manager

## 專案簡介

這是一個使用 Python PyQt6 開發的圖形化使用者介面 (GUI) 應用程式，旨在幫助開發者更方便地透過 PM2 管理專案 API。它提供了一個直觀的介面來監控和控制多個專案下的 API 服務。

## 核心功能

*   **API 列表與專案分類**: 清晰地列出所有 PM2 託管的 API，並按專案進行邏輯分組。
*   **詳細資訊與數據顯示**: 顯示每個 API 的詳細信息，包括名稱、PM2 ID、狀態、CPU/記憶體使用情況、重啟次數、運行時間、日誌路徑、專案路徑、端口、基本功能描述等。
*   **狀態燈號**: 以視覺化方式呈現 API 的運行狀態（如 `online`, `stopped`, `errored`）。
*   **API 控制**: 支援對單一 API 或整個專案下的所有 API 進行啟動、重啟、停止等操作。
*   **PM2 數據圖形化**: 實時顯示 CPU 和記憶體使用率的動態圓餅圖，方便監控性能。
*   **高度模組化**: 專案結構清晰，易於擴展和維護。

## 安裝指南

### 1. Python 版本要求

請確保您的系統已安裝 Python 3.9 或更高版本。

### 2. UV 虛擬環境建立

推薦使用 `uv` 來管理 Python 虛擬環境和依賴。如果您尚未安裝 `uv`，請先安裝它：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

然後，在專案根目錄下建立並啟動虛擬環境：

```bash
cd /Users/gamepig/projects/API_Manager # 進入專案根目錄
uv venv
source .venv/bin/activate
```

### 3. PM2 全局安裝

本應用程式依賴於 PM2 來管理 Node.js、Python、PHP 和 Go 等語言的 API 服務。請確保您的系統已全局安裝 PM2。

```bash
npm install pm2 -g
```

### 4. 安裝 Python 依賴

在啟動的虛擬環境中，安裝所有必要的 Python 套件：

```bash
uv pip install -r requirements.txt
```

### 5. 安裝 PHP (如果尚未安裝)

```bash
brew install php
```

### 6. 安裝 Go (如果尚未安裝)

```bash
brew install go
```

## 運行應用程式

在確保所有依賴都已安裝並在虛擬環境中後，您可以運行主應用程式：

```bash
python src/main_app.py
```

## 基本使用方式

1.  **API 列表**: 左側面板會顯示所有 PM2 託管的 API，並按專案名稱分組。您可以點擊專案名稱展開或收起其下的 API 列表。
2.  **查看 API 詳情**: 點擊左側列表中的任何 API 名稱，右側面板會顯示其詳細資訊，包括 CPU/記憶體使用圖表。
3.  **控制 API**: 點擊右側面板下方的「啟動」、「重啟」或「停止」按鈕來控制選定的 API。您也可以右鍵點擊專案名稱來批量啟動或停止該專案下的所有 API。

## 專案結構

```
API_Manager/
├── docs/                     # 專案文檔，如規劃書
├── dummy_api_project/        # 模擬 API 專案範例及 api.json 配置
│   └── docs/
│       └── api.json          # 模擬 API 的配置信息，包含端口和描述
├── src/                      # 應用程式源碼
│   ├── pm2_manager.py        # 與 PM2 交互的後端邏輯
│   ├── data_parser.py        # 數據解析與格式化
│   ├── gui_components.py     # PyQt6 GUI 元件
│   ├── main_app.py           # 主應用程式邏輯與 GUI 佈局
│   └── config.py             # 全局配置，如 API_CONFIGS
├── Task/                     # 開發任務分解與進度追蹤
├── tests/                    # 單元測試與整合測試
├── dummy_api.js              # 模擬 Node.js API 服務
├── dummy_apis.json           # PM2 批量啟動 dummy API 的配置檔
├── go_api                    # 編譯後的 Go API 可執行檔
├── go_api.go                 # 模擬 Go API 服務源碼
├── php_api.json              # PM2 啟動 PHP API 的配置檔
├── php_api.php               # 模擬 PHP API 服務源碼
├── python_api.py             # 模擬 Python API 服務源碼
└── requirements.txt          # Python 依賴清單
```

## 貢獻指南

(若未來開放協作，將在此處添加貢獻流程、程式碼提交規範等內容。) 