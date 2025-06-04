"""
config.py

此模組用於定義應用程式的配置變數。
"""

PM2_PATH = "/usr/local/bin/pm2"  # 根據實際 PM2 安裝路徑調整，或設置為 None 讓系統自動查找
"""
PM2 可執行文件的路徑。如果設置為 None，系統將會自動查找。
"""
API_METADATA_FILENAME = "api.json"
"""
API 元數據配置文件的檔案名稱。
"""
API_METADATA_DIRNAME = "docs"
"""
API 元數據配置文件所在的目錄名稱。
"""

API_CONFIGS = {
    # "api_name": {
    #     "port": "port_number",
    #     "description": "API description here"
    # }
}
"""
API 配置字典，用於儲存各個 API 的詳細資訊，如端口和描述。這是應用程式的預設配置，
也可以從 `dummy_api_project/docs/api.json` 載入。
"""