"""
data_parser.py

此模組負責解析從 PM2 命令獲取的 JSON 數據，並將其轉換為應用程式所需的結構化數據。
"""

import json
import os
from datetime import datetime
import re


def load_all_api_configs():
    """
    讀取 dummy_api_project/docs/api.json 檔案，獲取所有專案和 API 的配置資訊。

    Returns:
        dict: 包含所有專案和 API 配置的字典。如果檔案不存在、無法讀取或解析失敗，
              則返回空字典。
    
    Raises:
        json.JSONDecodeError: 如果 api.json 內容不是有效的 JSON 格式。
        Exception: 讀取檔案時發生任何其他未知錯誤。
    """
    api_json_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '..', 'dummy_api_project', 'docs', 'api.json')

    if not os.path.exists(api_json_path):
        print(f"錯誤：未找到 api.json 檔案於 {api_json_path}")
        return {}

    try:
        with open(api_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"錯誤：無法解析 {api_json_path} 的 JSON 數據。錯誤: {e}")
        return {}
    except Exception as e:
        print(f"讀取 {api_json_path} 時發生未知錯誤：{e}")
        return {}


def find_api_in_configs(api_name: str, all_api_configs: dict) -> \
        tuple[str, dict]:
    """
    從所有 API 配置中，根據 API 名稱找到其所屬的專案名稱及該 API 的詳細配置。

    Args:
        api_name (str): 要查找的 API 名稱。
        all_api_configs (dict): 包含所有專案和 API 配置的字典。

    Returns:
        tuple[str, dict]: 包含專案名稱和該 API 配置的元組。如果未找到，
                          則返回 ("Unknown Project", {})。
    """
    for project_name, apis in all_api_configs.items():
        if api_name in apis:
            return project_name, apis[api_name]
    return "Unknown Project", {}


def parse_pm2_list_output(api_list: list) -> list:
    """
    解析 'pm2 list --json' 命令的 JSON 輸出（已預先解析），並提取相關 API 服務資訊。

    Args:
        api_list (list): 從 pm2 list --json 命令獲取並已解析的 Python 列表。

    Returns:
        list: 包含解析後 API 服務資訊的字典列表。
              如果解析失敗或輸出格式不正確，則返回空列表。

    Raises:
        Exception: 解析 PM2 數據時發生任何未知錯誤。
    """
    parsed_data = []
    all_api_configs = load_all_api_configs()  # 載入所有 API 配置一次

    try:
        for api in api_list:
            api_name = api.get('name')
            project_name, api_config = find_api_in_configs(
                api_name, all_api_configs)

            api_info = {
                "name": api_name,
                "pm_id": api.get('pm_id'),
                "status": api.get('pm2_env', {}).get('status', 'unknown'),
                "cpu": api.get('monit', {}).get('cpu', 0),
                "memory": api.get('monit', {}).get('memory', 0),  # Bytes
                "restarts": api.get('restart_time', 0),
                "cpu_history": api.get('cpu_history', []),
                "memory_history": api.get('memory_history', []),
                "time_history": api.get('time_history', []),
                "uptime": get_api_uptime(api),  # 使用新的函數來計算運行時間
                "log_file_path": (api.get('pm2_env', {}).get('pm_out_log_path') or
                                  api.get('pm2_env', {}).get('log_file') or "N/A"),
                "project_path": (api.get('pm_exec_path') or
                                 api.get('pm2_env', {}).get('PWD') or
                                 os.path.dirname(
                                     api.get('pm2_env', {}).get('script', ''))),
                "project_name": project_name,  # 從 api.json 獲取的專案名稱
                "port": get_api_port(api, api_config),  # 傳遞 api_config
                "description": get_api_description(api, api_config),  # 傳遞 api_config
                "metadata": api_config  # 直接將 api_config 作為 metadata
            }
            parsed_data.append(api_info)
    except Exception as e:
        print(f"解析 PM2 數據時發生未知錯誤：{e}")

    return parsed_data


def get_project_name(api: dict, all_api_configs: dict) -> str:
    """
    從 API 資訊中提取專案名稱。

    Args:
        api (dict): 單個 API 的 PM2 資訊字典。
        all_api_configs (dict): 包含所有專案和 API 配置的字典。

    Returns:
        str: 提取到的專案名稱，如果無法確定則返回 "Unknown Project"。
    """
    api_name = api.get('name')
    project_name, _ = find_api_in_configs(api_name, all_api_configs)
    return project_name


def get_api_port(api: dict, api_config: dict) -> str:
    """
    從 API 資訊中提取端口號。
    優先從 api_config 中獲取端口。
    如果沒有，嘗試從 pm2_env.args 中獲取 --port 參數。
    最後，如果都沒有，返回 'N/A'。

    Args:
        api (dict): 單個 API 的 PM2 資訊字典。
        api_config (dict): 該 API 在 api.json 中的配置字典。

    Returns:
        str: 提取到的端口號字串，如果無法確定則返回 "N/A"。
    """
    # 優先從 api_config 中獲取端口
    port_from_config = api_config.get('port')
    if port_from_config:
        return str(port_from_config)

    # 嘗試從 pm2_env.args 中獲取端口
    args = api.get('pm2_env', {}).get('args', [])
    try:
        if isinstance(args, list):
            # 嘗試從 --port 參數中獲取端口
            port_index = args.index('--port')
            if port_index != -1 and port_index + 1 < len(args):
                return str(args[port_index + 1])

            # 如果沒有 --port，嘗試從類似 'localhost:port' 的參數中提取端口
            for arg in args:
                match = re.search(r':(\d+)$', arg)
                if match:
                    return match.group(1)
    except ValueError:
        pass
    except Exception as e:
        print(f"提取端口時發生錯誤: {e}")

    return "N/A"


def get_api_description(api: dict, api_config: dict) -> str:
    """
    從 API 資訊中提取功能描述。
    優先從 api_config 中獲取。
    如果沒有，返回一個預設描述。

    Args:
        api (dict): 單個 API 的 PM2 資訊字典。
        api_config (dict): 該 API 在 api.json 中的配置字典。

    Returns:
        str: API 的功能描述字串，如果沒有則返回 "無描述"。
    """
    description_from_config = api_config.get('description')
    if description_from_config:
        return description_from_config

    return "無描述"


def load_api_metadata(project_path: str) -> dict:
    """
    讀取指定專案目錄下的 api.json 檔案，獲取 API 的變更與詳細資料。
    注意：此函數可能已被 load_all_api_configs() 取代，請確認其用途。

    Args:
        project_path (str): 專案的根目錄路徑。

    Returns:
        dict: 解析後的 api.json 內容，如果檔案不存在或解析失敗則返回空字典。
    
    Raises:
        json.JSONDecodeError: 如果 api.json 內容不是有效的 JSON 格式。
        Exception: 讀取檔案時發生任何其他未知錯誤。
    """
    if not project_path or project_path == "N/A":
        return {}

    api_json_path = os.path.join(
        project_path, 'dummy_api_project', 'docs', 'api.json')

    if not os.path.exists(api_json_path):
        return {}

    try:
        with open(api_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"錯誤：無法解析 {api_json_path} 的 JSON 數據。錯誤: {e}")
        return {}
    except Exception as e:
        print(f"讀取 {api_json_path} 時發生未知錯誤：{e}")
        return {}


def get_api_uptime(api: dict) -> str:
    """
    從 API 資訊中提取運行時間並格式化。

    Args:
        api (dict): 單個 API 的 PM2 資訊字典。

    Returns:
        str: 格式化的運行時間字串 (例如 "1 天 2 小時 30 分 15 秒")。
             如果 API 狀態為 "stopped" 或無法確定運行時間，則返回 "N/A"。
    """
    status = api.get('pm2_env', {}).get('status', 'unknown')
    if status == 'stopped':
        return "N/A"

    created_at = api.get('pm2_env', {}).get('created_at')
    if created_at:
        try:
            # pm2_env.created_at 是一個 Unix 時間戳 (毫秒)
            start_time = datetime.fromtimestamp(created_at / 1000)
            current_time = datetime.now()
            uptime_delta = current_time - start_time

            days = uptime_delta.days
            hours = uptime_delta.seconds // 3600
            minutes = (uptime_delta.seconds % 3600) // 60
            seconds = uptime_delta.seconds % 60

            parts = []
            if days > 0:
                parts.append(f"{days} 天")
            if hours > 0:
                parts.append(f"{hours} 小時")
            if minutes > 0:
                parts.append(f"{minutes} 分")
            if seconds > 0:
                parts.append(f"{seconds} 秒")

            if not parts:
                return "0 秒"  # Less than a second
            return " ".join(parts)
        except Exception as e:
            print(f"計算運行時間時發生錯誤: {e}")
            return "N/A"
    return "N/A"