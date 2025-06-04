# 3. 前端 GUI 開發

本階段將專注於構建 PM2 API 管理頁面的圖形使用者介面，實現數據的視覺化展示和用戶交互功能。

## 3.1 基礎 GUI 框架搭建 (`main_app.py`)

*   [x] 建立 `src/main_app.py` 檔案。
*   [x] 匯入必要的 PyQt6 模組 (例如 `QApplication`, `QWidget`, `QVBoxLayout`, `QHBoxLayout`, `QPushButton`, `QLabel`, `QTableWidget` 等)。
*   [x] 建立主視窗類別，繼承自 `QWidget` 或 `QMainWindow`。
*   [x] 初始化主視窗，設定標題、尺寸。
*   [x] 設計整體佈局，包含：
    *   頂部：標題、全局控制按鈕 (例如「全部啟動」、「全部重啟」、「全部停止」)。
    *   左側：API 列表區域 (按專案分類顯示)。
    *   右側：選定 API 的詳細資訊和數據圖表顯示區域。
*   [x] 實現基本的事件循環，讓應用程式可以運行。

## 3.2 可重複使用 GUI 組件 (`gui_components.py`)

*   [x] 建立 `src/gui_components.py` 檔案。
*   [x] 實作 `ApiStatusLight` 組件：一個繼承自 `QLabel` 或 `QWidget` 的小部件，根據傳入的狀態 (運行中、已停止、有問題) 顯示綠、紅、黃色的圓點或方塊。
*   [x] 實作 `ApiDataTable` 組件：一個繼承自 `QTableWidget` 的組件，用於顯示 API 列表，包含 API 名稱、專案、狀態。
*   [x] 實作 `ApiDetailPanel` 組件：一個繼承自 `QWidget` 的組件，用於顯示單個 API 的詳細資訊 (PID, 記憶體, CPU, 運行時間, 重啟次數, 日誌路徑, 專案路徑)。
*   [x] 實作 `PerformanceGraph` 組件：一個繼承自 `QWidget` 的組件，整合 Matplotlib 或 Plotly，用於繪製 CPU 和記憶體使用率的歷史趨勢圖。

## 3.3 API 列表與狀態顯示

*   [x] 在 `main_app.py` 中，整合 `pm2_manager.py` 獲取 API 列表的邏輯。
*   [x] 將獲取的 API 列表動態填充到 `ApiDataTable` 組件中。
*   [x] 為每個 API 項目動態創建並顯示 `ApiStatusLight` 組件，根據其 PM2 狀態實時更新顏色。
*   [x] 實現按專案分類顯示 API 的邏輯 (例如使用 `QTreeWidget` 或分組 `QTableWidget` 行)。

## 3.4 API 詳細資訊與數據圖形化

*   [x] 實現當用戶點擊 `ApiDataTable` 中的 API 項目時，觸發事件來更新右側的詳細資訊顯示。
*   [x] 從選定的 API 數據中提取詳細資訊，並填充到 `ApiDetailPanel` 組件中。
*   [x] 將歷史 CPU 和記憶體數據傳遞給 `PerformanceGraph` 組件，並繪製相應的趨勢圖。
*   [x] 實現數據的定時更新機制，以確保顯示的資訊是即時的。

## 3.5 API 控制介面

*   [x] 在 `ApiDetailPanel` 或相關位置添加「啟動」、「重啟」、「停止」按鈕，並綁定 `pm2_manager.py` 中的單個 API 控制函數。
*   [x] 在主視窗頂部或特定區域添加專案層級的「一鍵啟動」、「一鍵重啟」、「一鍵停止」按鈕，並綁定 `pm2_manager.py` 中的批量控制函數。
*   [x] 實作操作後的結果回饋機制，例如彈出提示訊息或更新狀態燈。

## 3.6 單元測試 (Frontend)

*   [x] **視覺組件測試：**
    *   [x] 為 `ApiStatusLight` 組件編寫測試，驗證在不同狀態下是否顯示正確的顏色。
    *   [x] 測試 `ApiDataTable` 組件是否能正確填充和顯示數據，以及點擊事件是否正常觸發。
    *   [x] 測試 `ApiDetailPanel` 組件是否能正確顯示傳入的 API 詳細資訊。
    *   [x] 測試 `PerformanceGraph` 組件是否能接收數據並正確繪製圖表 (可能需要模擬 Matplotlib 的繪圖輸出)。
*   [x] **事件處理測試：**
    *   [x] 測試點擊控制按鈕後是否正確調用後端 `pm2_manager` 的功能。
    *   [ ] 測試數據更新機制是否按預期工作。

## 3.7 實際測試 (Frontend)

*   [x] 運行應用程式，驗證界面是否正常顯示，佈局是否美觀。
*   [ ] 手動啟動、停止、重啟幾個 PM2 託管的 API，觀察界面上狀態燈是否實時變化。
*   [ ] 點擊不同 API 項目，驗證右側詳細資訊面板是否正確顯示，且數據圖表是否正確繪製。
*   [ ] 測試專案層級的批量控制功能，驗證是否能同時控制多個 API。
*   [ ] 嘗試在 API 服務崩潰時，觀察狀態燈是否變為黃色，並驗證重啟功能是否正常。
*   [ ] 模擬不同的 PM2 列表輸出，驗證界面是否能正確響應和更新。 