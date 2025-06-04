"""
pm2_manager.py

此模組負責與 PM2 進行交互，提供獲取 PM2 託管的 API 服務列表、啟動、重啟、停止等功能。
""" 

import subprocess
import json
import os
from datetime import datetime
from collections import deque
from src import data_parser

# 用於儲存 API 歷史數據的字典
# 每個 API 的歷史數據將是一個 deque，限制其大小以避免記憶體無限增長
_api_history_data = {}
MAX_HISTORY_POINTS = 60 # 儲存最近 60 個數據點 (例如 60 秒的數據)

def get_pm2_list():
    """
    執行 'pm2 jlist' 命令並解析輸出，同時更新 API 歷史數據。

    Returns:
        list: 包含 PM2 託管的 API 服務資訊的字典列表。
              如果命令執行失敗或輸出解析失敗，則返回空列表。
    """
    global _api_history_data
    try:
        command = ["pm2", "jlist"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        raw_list = json.loads(result.stdout)

        # 更新歷史數據
        for api in raw_list:
            pm_id = api.get('pm_id')
            cpu = api.get('monit', {}).get('cpu', 0)
            memory = api.get('monit', {}).get('memory', 0)
            # 確保 memory 是整數，以避免類型錯誤
            if isinstance(memory, str):
                try:
                    memory = int(memory)
                except ValueError:
                    memory = 0 # 如果無法轉換為整數，則預設為 0
            timestamp = datetime.now().strftime("%H:%M:%S")

            if pm_id not in _api_history_data:
                _api_history_data[pm_id] = {
                    'cpu_history': deque(maxlen=MAX_HISTORY_POINTS),
                    'memory_history': deque(maxlen=MAX_HISTORY_POINTS),
                    'time_history': deque(maxlen=MAX_HISTORY_POINTS)
                }

            _api_history_data[pm_id]['cpu_history'].append(cpu)
            _api_history_data[pm_id]['memory_history'].append(memory / (1024 * 1024)) # 將位元組轉換為 MB
            _api_history_data[pm_id]['time_history'].append(timestamp)
        
        # 將歷史數據添加到每個 API 字典中，以便 data_parser 處理
        for api in raw_list:
            pm_id = api.get('pm_id')
            if pm_id in _api_history_data:
                api['cpu_history'] = list(_api_history_data[pm_id]['cpu_history'])
                api['memory_history'] = list(_api_history_data[pm_id]['memory_history'])
                api['time_history'] = list(_api_history_data[pm_id]['time_history'])
            else:
                api['cpu_history'] = []
                api['memory_history'] = []
                api['time_history'] = []

        return raw_list
    except FileNotFoundError:
        print("錯誤：PM2 命令未找到。請確認 PM2 已全局安裝。")
        return []
    except subprocess.CalledProcessError as e:
        print(f"錯誤：執行 PM2 命令失敗。錯誤訊息：{e.stderr}")
        return []
    except json.JSONDecodeError:
        print("錯誤：無法解析 PM2 輸出的 JSON 數據。")
        return []
    except Exception as e:
        print(f"發生未知錯誤：{e}")
        return []

def start_api(name_or_id):
    """
    啟動指定的 PM2 API 服務。

    Args:
        name_or_id (str): API 的名稱或 PM2 ID。

    Returns:
        bool: 如果命令執行成功則返回 True，否則返回 False。
    """
    try:
        command = ["pm2", "start", str(name_or_id)]
        subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"成功啟動 API: {name_or_id}")
        return True
    except FileNotFoundError:
        print("錯誤：PM2 命令未找到。請確認 PM2 已全局安裝。")
        return False
    except subprocess.CalledProcessError as e:
        print(f"錯誤：啟動 API {name_or_id} 失敗。錯誤訊息：{e.stderr}")
        return False
    except Exception as e:
        print(f"啟動 API {name_or_id} 時發生未知錯誤：{e}")
        return False

def restart_api(name_or_id):
    """
    重啟指定的 PM2 API 服務。

    Args:
        name_or_id (str): API 的名稱或 PM2 ID。

    Returns:
        bool: 如果命令執行成功則返回 True，否則返回 False。
    """
    try:
        command = ["pm2", "restart", str(name_or_id)]
        subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"成功重啟 API: {name_or_id}")
        return True
    except FileNotFoundError:
        print("錯誤：PM2 命令未找到。請確認 PM2 已全局安裝。")
        return False
    except subprocess.CalledProcessError as e:
        print(f"錯誤：重啟 API {name_or_id} 失敗。錯誤訊息：{e.stderr}")
        return False
    except Exception as e:
        print(f"重啟 API {name_or_id} 時發生未知錯誤：{e}")
        return False

def stop_api(name_or_id):
    """
    停止指定的 PM2 API 服務。

    Args:
        name_or_id (str): API 的名稱或 PM2 ID。

    Returns:
        bool: 如果命令執行成功則返回 True，否則返回 False。
    """
    try:
        command = ["pm2", "stop", str(name_or_id)]
        subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"成功停止 API: {name_or_id}")
        return True
    except FileNotFoundError:
        print("錯誤：PM2 命令未找到。請確認 PM2 已全局安裝。")
        return False
    except subprocess.CalledProcessError as e:
        print(f"錯誤：停止 API {name_or_id} 失敗。錯誤訊息：{e.stderr}")
        return False
    except Exception as e:
        print(f"停止 API {name_or_id} 時發生未知錯誤：{e}")
        return False

def start_project_apis(project_name):
    """
    根據專案名稱批量啟動所有相關 API 服務。

    Args:
        project_name (str): 專案的名稱。

    Returns:
        bool: 如果所有相關 API 服務成功啟動則返回 True，否則返回 False。
    """
    pm2_list = get_pm2_list()
    if not pm2_list:
        print("沒有找到任何 PM2 託管的 API 服務。")
        return False

    all_api_configs = data_parser.load_all_api_configs()

    success = True
    apis_found_for_project = False
    for api in pm2_list:
        if data_parser.get_project_name(api, all_api_configs).lower() == project_name.lower():
            apis_found_for_project = True
            api_id = api.get('pm_id')
            api_name = api.get('name')
            print(f"嘗試啟動專案 '{project_name}' 中的 API: {api_name} (ID: {api_id})")
            if not start_api(api_id):
                success = False
                print(f"啟動 API: {api_name} (ID: {api_id}) 失敗。")
    
    if not apis_found_for_project:
        print(f"未找到專案 '{project_name}' 下的任何 API 服務。")
        return False # If no APIs found, or if any failed and no APIs were found for the project

    return success

def restart_project_apis(project_name):
    """
    根據專案名稱批量重啟所有相關 API 服務。

    Args:
        project_name (str): 專案的名稱。

    Returns:
        bool: 如果所有相關 API 服務成功重啟則返回 True，否則返回 False。
    """
    pm2_list = get_pm2_list()
    if not pm2_list:
        print("沒有找到任何 PM2 託管的 API 服務。")
        return False

    all_api_configs = data_parser.load_all_api_configs()

    success = True
    apis_found_for_project = False
    for api in pm2_list:
        if data_parser.get_project_name(api, all_api_configs).lower() == project_name.lower():
            apis_found_for_project = True
            api_id = api.get('pm_id')
            api_name = api.get('name')
            print(f"嘗試重啟專案 '{project_name}' 中的 API: {api_name} (ID: {api_id})")
            if not restart_api(api_id):
                success = False
                print(f"重啟 API: {api_name} (ID: {api_id}) 失敗。")
    
    if not apis_found_for_project:
        print(f"未找到專案 '{project_name}' 下的任何 API 服務。")
        return False

    return success

def stop_project_apis(project_name):
    """
    根據專案名稱批量停止所有相關 API 服務。

    Args:
        project_name (str): 專案的名稱。

    Returns:
        bool: 如果所有相關 API 服務成功停止則返回 True，否則返回 False。
    """
    pm2_list = get_pm2_list()
    if not pm2_list:
        print("沒有找到任何 PM2 託管的 API 服務。")
        return False

    all_api_configs = data_parser.load_all_api_configs()

    success = True
    apis_found_for_project = False
    for api in pm2_list:
        if data_parser.get_project_name(api, all_api_configs).lower() == project_name.lower():
            apis_found_for_project = True
            api_id = api.get('pm_id')
            api_name = api.get('name')
            print(f"嘗試停止專案 '{project_name}' 中的 API: {api_name} (ID: {api_id})")
            if not stop_api(api_id):
                success = False
                print(f"停止 API: {api_name} (ID: {api_id}) 失敗。")

    if not apis_found_for_project:
        print(f"未找到專案 '{project_name}' 下的任何 API 服務。")
        return False

    return success

def get_all_project_names():
    """
    獲取所有已知的專案名稱。

    Returns:
        set: 包含所有專案名稱的集合。
    """
    pm2_list = get_pm2_list()
    if not pm2_list:
        return set()

    all_api_configs = data_parser.load_all_api_configs()
    project_names = set()
    for api in pm2_list:
        project_name = data_parser.get_project_name(api, all_api_configs)
        if project_name and project_name != "Unknown Project":
            project_names.add(project_name)
    return project_names