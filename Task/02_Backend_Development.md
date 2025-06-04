# 2. 後端核心功能開發

本階段將專注於開發 PM2 API 管理頁面的後端核心邏輯，包含與 PM2 的交互、數據解析以及 API 資訊的整合。

## 2.1 PM2 交互模組 (`pm2_manager.py`)

*   [x] 建立 `src/pm2_manager.py` 檔案。
*   [x] 實作 `get_pm2_list()` 函數，用於執行 `pm2 list --json` 命令並捕獲輸出。
*   [x] 實作 `start_api(name_or_id)` 函數，用於執行 `pm2 start <name_or_id>` 命令。
*   [x] 實作 `restart_api(name_or_id)` 函數，用於執行 `pm2 restart <name_or_id>` 命令。
*   [x] 實作 `stop_api(name_or_id)` 函數，用於執行 `pm2 stop <name_or_id>` 命令。
*   [x] 實作 `start_project_apis(project_name)` 函數，根據專案名稱批量啟動所有相關 API 服務。
*   [x] 實作 `restart_project_apis(project_name)` 函數，根據專案名稱批量重啟所有相關 API 服務。
*   [x] 實作 `stop_project_apis(project_name)` 函數，根據專案名稱批量停止所有相關 API 服務。
*   [x] 實作錯誤處理機制，捕獲 PM2 命令執行失敗的情況。

## 2.2 數據解析模組 (`data_parser.py`)

*   [x] 建立 `src/data_parser.py` 檔案。
*   [x] 實作 `parse_pm2_list_output(json_output)` 函數，解析 `pm2 list --json` 的 JSON 輸出，並提取以下資訊：
    *   API 名稱 (name)
    *   PM2 Process ID (pm_id)
    *   狀態 (status)
    *   CPU 使用率 (cpu)
    *   記憶體使用量 (memory)
    *   運行時間 (uptime)
    *   重啟次數 (restarts)
    *   日誌路徑 (log_file_path)
    *   專案路徑 (pm2_env.PWD 或 script)
*   [x] 實作 `get_project_name(api_data)` 函數，從 API 數據中提取或推斷所屬專案名稱（基於檔案路徑或其他約定）。
*   [x] **整合 `api.json` 數據：**
    *   [x] 實作 `load_api_metadata(project_path)` 函數，讀取每個專案 `docs/` 目錄下的 `api.json` 檔案，獲取 API 的變更與詳細資料。
    *   [x] 設計一個數據結構，將 PM2 監控數據與 `api.json` 中的元數據（如 API 描述、變更歷史等）進行整合，以便前端統一展示。

## 2.3 配置模組 (`config.py`)

*   [x] 建立 `src/config.py` 檔案。
*   [x] 定義應用程式所需的配置變數，例如：
    *   PM2 命令的路徑 (如果 PM2 不在系統 PATH 中)。
    *   `api.json` 檔案的預期相對路徑 (例如 `docs/api.json`)。

## 2.4 後端單元測試
- [x] 為 `pm2_manager.py` 中的所有函數編寫單元測試。
  - [x] `get_pm2_list()`
  - [x] `start_api()`
  - [x] `restart_api()`
  - [x] `stop_api()`
  - [x] `start_project_apis()`
  - [x] `restart_project_apis()`
  - [x] `stop_project_apis()`
- [x] 為 `data_parser.py` 中的所有函數編寫單元測試。
  - [x] `parse_pm2_list_output()`
  - [x] `get_project_name()`
  - [x] `load_api_metadata()`
- [x] 為 `config.py` 編寫單元測試 (如果需要)。

## 2.5 實際測試 (Backend)

*   [x] 模擬 PM2 環境，啟動虛擬 API 服務，並建立虛擬 `api.json` 檔案。
*   [x] 執行 `pm2_manager.py` 和 `data_parser.py` 的功能，驗證其在模擬環境下的行為。
*   [x] 驗證 PM2 狀態變化，確認控制命令（啟動、重啟、停止）的有效性。
*   [x] 模擬錯誤情況，測試錯誤處理機制。 