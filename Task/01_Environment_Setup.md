# 1. 環境設定與專案初始化

本階段主要目標是建立與配置開發環境，並初始化專案的基本結構與版本控制。

## 1.1 建立專案目錄結構

*   [x] 確認 `API_Manager/src/` 目錄已建立。
*   [x] 確認 `API_Manager/tests/` 目錄已建立。
*   [x] 確認 `API_Manager/docs/` 目錄已建立。
*   [x] 確認 `API_Manager/Task/` 目錄已建立。

## 1.2 建立 Python 虛擬環境 (UV)

*   [x] 在專案根目錄 `/Users/gamepig/projects/API_Manager/` 下使用 UV 建立新的虛擬環境。
    ```bash
    cd /Users/gamepig/projects/API_Manager && uv venv
    ```
*   [x] 啟動虛擬環境 (開發時手動執行，CI/CD 環境會自動處理)。
    ```bash
    source .venv/bin/activate
    ```

## 1.3 PM2 全局安裝

*   [x] 確保系統上已全局安裝 PM2。如果尚未安裝，請執行以下命令：
    ```bash
    npm install pm2 -g
    ```
*   [x] 驗證 PM2 是否正確安裝，執行 `pm2 --version`。

## 1.4 安裝基本依賴

*   [x] 在虛擬環境中，使用 `uv pip install` 安裝 GUI 框架、數據圖形化及系統資訊獲取所需的基本 Python 套件。
    *   `pyqt6`：用於 GUI 界面。
    *   `matplotlib`：用於數據圖形化。
    *   `psutil`：用於獲取系統資源使用情況 (如果 PM2 數據不夠詳細)。
    ```bash
    cd /Users/gamepig/projects/API_Manager && source .venv/bin/activate && uv pip install pyqt6 matplotlib psutil
    ```
*   [x] 創建 `requirements.txt` 檔案，記錄專案依賴。
    ```bash
    cd /Users/gamepig/projects/API_Manager && source .venv/bin/activate && uv pip freeze > requirements.txt
    ```

## 1.5 Git 初始化與首次提交

*   [x] 在專案根目錄下初始化 Git 倉庫 (如果尚未初始化)。
    ```bash
    cd /Users/gamepig/projects/API_Manager && git init
    ```
*   [x] 創建 `.gitignore` 檔案，忽略虛擬環境 (`.venv/`)、Python 編譯文件 (`__pycache__/`, `*.pyc`) 及 macOS 特有檔案 (`.DS_Store`) 等不需版本控制的檔案。
*   [x] 設定 Git 遠端倉庫 (`origin`)，並將本地 `main` 分支推送到遠端倉庫。
    ```bash
    cd /Users/gamepig/projects/API_Manager && git remote add origin <您的Git倉庫URL>
    git branch -M main
    git push -u origin main
    ```
*   [x] 提交所有初始檔案 (規劃書、專案結構、`.gitignore`、`requirements.txt` 等) 到 Git 倉庫。
    ```bash
    cd /Users/gamepig/projects/API_Manager && git add .
    git commit -m "feat: 初始化專案環境，包含目錄結構、虛擬環境與Git設定"
    git push
    ```

## 1.6 單元測試 (環境設定)

*   [x] **無特定單元測試：** 環境設定階段主要為準備工作，不涉及可單元測試的程式碼邏輯。

## 1.7 實際測試 (環境設定)

*   [x] **驗證目錄結構：** 確認 `src/`, `tests/`, `docs/`, `Task/` 等目錄已正確創建。
    ```bash
    ls -l /Users/gamepig/projects/API_Manager/
    ```
*   [x] **驗證虛擬環境：** 確認 `.venv/` 資料夾存在，且可以成功啟動虛擬環境。
    ```bash
    ls -l /Users/gamepig/projects/API_Manager/.venv/
    source /Users/gamepig/projects/API_Manager/.venv/bin/activate && python --version
    ```
*   [x] **驗證 PM2 安裝：** 確認 PM2 已全局安裝且命令可用。
    ```bash
    pm2 --version
    ```
*   [x] **驗證依賴安裝：** 確認 `pyqt6`, `matplotlib`, `psutil` 等套件在虛擬環境中可用。
    ```bash
    source /Users/gamepig/projects/API_Manager/.venv/bin/activate && python -c "import PyQt6; import matplotlib; import psutil; print('All modules imported successfully')"
    ```
*   [x] **驗證 Git 倉庫狀態：** 確認 `.git/` 資料夾存在，且首次提交已成功推送到遠端倉庫。
    ```bash
    ls -l /Users/gamepig/projects/API_Manager/.git/
    git status
    git log --oneline
    ``` 