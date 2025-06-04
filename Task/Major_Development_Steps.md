# PM2 API 管理頁面 - 主要開發步驟

本文件將根據規劃書，將 PM2 API 管理頁面的開發流程劃分為幾個主要階段，並詳細列出每個階段的子步驟，同時整合 Git 版本控制與 CI/CD 設定。

---

## 主要開發階段：

*   [1. 環境設定與專案初始化](01_Environment_Setup.md)
*   [2. 後端核心功能開發](02_Backend_Development.md)
*   [3. 前端 GUI 開發](03_Frontend_GUI_Development.md)
*   [4. 測試](04_Testing.md)
*   [X] [5. 文件與維護](05_Documentation_and_Maintenance.md)
*   [X] [6. 版本控制與持續整合/部署 (CI/CD)](06_CI_CD_Setup.md)
*   [ ] [7. 待辦事項 (TBD)](07_ToDo.md)

---

**重要提示：PM2 全局安裝**

在開始開發之前，請確保您的系統上已全局安裝 PM2。如果尚未安裝，請執行以下命令：

```bash
npm install pm2 -g
```

這將確保 PM2 命令在任何路徑下都可執行，方便後續的 PM2 交互操作。

## 1. 環境設定與專案初始化

### 1.1 建立專案目錄結構
*   根據規劃書的「5. 專案結構」創建 `src/` 和 `tests/` 等目錄。

### 1.2 建立 Python 虛擬環境 (UV)
*   在專案根目錄下使用 UV 建立新的虛擬環境。
    ```bash
    uv venv
    source .venv/bin/activate
    ```

### 1.3 安裝基本依賴
*   安裝 PM2 互動、數據處理及 GUI 框架所需的基本 Python 套件。
    *   例如：`pip install pyqt5` (或 `pyside6`), `pip install matplotlib`, `pip install psutil` (用於獲取系統資源，若 PM2 數據不夠詳細)。

### 1.4 Git 初始化與首次提交
*   初始化 Git 倉庫。
    ```bash
    git init
    ```
*   創建 `.gitignore` 檔案，忽略虛擬環境、PyInstaller 輸出等不需版本控制的檔案。
*   將規劃書、專案結構等首次提交至 Git 倉庫。
    ```bash
    git add .
    git commit -m "feat: 初始化專案並新增規劃書與基本結構"
    git branch -M main
    git remote add origin <您的Git倉庫URL>
    git push -u origin main
    ```

## 2. 後端核心功能開發

### 2.1 PM2 交互模組 (`pm2_manager.py`)
*   實現 PM2 列表獲取功能 (`pm2 list --json`)。
*   實現 PM2 進程控制功能 (啟動 `pm2 start`, 重啟 `pm2 restart`, 停止 `pm2 stop`)。
*   實現根據專案名稱批量控制 API 的邏輯。

### 2.2 數據解析模組 (`data_parser.py`)
*   解析 `pm2 list --json` 的輸出，提取 API 名稱、PID、狀態、CPU、記憶體等關鍵資訊。
*   設計數據結構，便於前端展示和處理。

### 2.3 配置模組 (`config.py`)
*   定義應用程式所需的配置，例如 PM2 命令路徑 (若非全局安裝) 等。

### 2.4 單元測試 (Backend)
*   為 `pm2_manager.py` 和 `data_parser.py` 編寫單元測試。
*   確保與 PM2 的交互和數據解析的正確性。

## 3. 前端 GUI 開發

### 3.1 基礎 GUI 框架搭建 (`main_app.py`)
*   使用選定的 GUI 框架 (例如 PyQt5/PySide6) 搭建主視窗。
*   設計整體佈局，包含 API 列表區域、詳細資訊顯示區域、控制按鈕等。

### 3.2 可重複使用 GUI 組件 (`gui_components.py`)
*   開發 API 狀態燈組件 (根據狀態顯示綠、紅、黃燈)。
*   開發數據圖表組件，用於顯示 CPU 和記憶體使用趨勢。

### 3.3 API 列表與狀態顯示
*   將後端獲取的 API 列表展示在 GUI 上，並實時更新狀態。
*   實現依專案分類顯示 API 的邏輯。

### 3.4 API 詳細資訊與數據圖形化
*   實現點擊 API 項目後，在詳細資訊區域顯示其 PM2 數據。
*   將 CPU 和記憶體使用率以圖表形式展示。

### 3.5 API 控制介面
*   為單個 API 和專案提供啟動、重啟、停止按鈕，並綁定後端功能。

## 4. 測試

### 4.1 整合測試
*   測試前後端模組的整合，確保數據流和控制指令的正確傳遞。

### 4.2 UI/UX 測試
*   進行使用者介面和使用者體驗測試，確保應用程式易用、直觀。

### 4.3 效能測試
*   在高 API 數量情境下，測試應用程式的響應速度和資源佔用。

## 5. 文件與維護

### 5.1 更新 `README.md`
*   提供詳細的安裝、運行、使用指南。
*   包含開發環境設定、依賴安裝、專案結構說明等。

### 5.2 程式碼註解與文檔
*   為關鍵模組和函數編寫清晰的註解和文檔字符串 (docstrings)。

## 6. 版本控制與持續整合/部署 (CI/CD)

### 6.1 Git 工作流程
*   採用 Git Flow 或 GitHub Flow 等工作流程，管理分支 (main, develop, feature, hotfix)。
*   定期將開發進度推送到遠程倉庫。
    ```bash
    git push origin <branch_name>
    ```

### 6.2 CI/CD 設定
*   選擇合適的 CI/CD 工具 (例如 GitHub Actions, GitLab CI/CD, Jenkins)。
*   設定 CI 流程：
    *   **觸發器：** 每次 `push` 到特定分支 (例如 `develop` 或 `main`) 或提交 Pull Request 時觸發。
    *   **環境準備：** 安裝 Python、UV、PM2 (模擬或實際環境) 等。
    *   **依賴安裝：** `uv pip install -r requirements.txt`。
    *   **程式碼品質檢查：** 執行 `flake8`, `pylint` 等工具。
    *   **運行測試：** 執行單元測試和整合測試。
    *   **構建打包 (若有)：** 若需發布桌面應用，可在此步驟使用 PyInstaller 等工具打包應用程式。
*   設定 CD 流程 (可選，根據部署方式)：
    *   **部署：** 將打包好的應用程式部署到測試環境或生產環境。

## 7. 待辦事項 (TBD)

*   根據實際開發進度，補充更詳細的子任務。
*   針對特定技術選型 (例如 PyQt5 的具體組件使用) 進行細化。 