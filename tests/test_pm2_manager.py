"""
test_pm2_manager.py

此模組包含 `pm2_manager.py` 的單元測試。
""" 

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
import subprocess

# 將專案根目錄添加到 sys.path，以便找到 src 模組
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pm2_manager import get_pm2_list, start_api, restart_api, stop_api, \
                          start_project_apis, restart_project_apis, stop_project_apis
from src import config

class TestPM2Manager(unittest.TestCase):

    def setUp(self):
        # Backup original PM2_PATH and set it for testing
        self.original_pm2_path = getattr(config, 'PM2_PATH', None)
        config.PM2_PATH = "pm2" # For testing, assume pm2 is in PATH

    def tearDown(self):
        # Restore original PM2_PATH
        if self.original_pm2_path is not None:
            config.PM2_PATH = self.original_pm2_path

    @patch('subprocess.run')
    def test_get_pm2_list(self, mock_subprocess_run):
        # Mock the output of pm2 list --json
        mock_pm2_output = """
        [
            {
                "name": "dummy-api-1",
                "pm_id": 0,
                "status": "online",
                "pid": 1234,
                "monit": {"cpu": "0.5%", "memory": "20.0 MB"},
                "pm2_env": {"HOME": "/home/user", "log_file": "/path/to/log1.log", "pm_uptime": 1678886400000, "unstable_restarts": 0, "pm_cwd": "/Users/gamepig/projects/API_Manager/dummy_api_project"}
            },
            {
                "name": "another-api",
                "pm_id": 1,
                "status": "stopped",
                "pid": 5678,
                "monit": {"cpu": "0%", "memory": "0 MB"},
                "pm2_env": {"HOME": "/home/user", "log_file": "/path/to/log2.log", "pm_uptime": 0, "unstable_restarts": 5, "pm_cwd": "/Users/gamepig/projects/API_Manager/another_project"}
            }
        ]
        """
        mock_subprocess_run.return_value = MagicMock(stdout=mock_pm2_output)

        pm2_list = get_pm2_list()

        mock_subprocess_run.assert_called_once_with(["pm2", "jlist"], capture_output=True, text=True, check=True)

        self.assertEqual(len(pm2_list), 2)
        self.assertEqual(pm2_list[0]['name'], 'dummy-api-1')
        self.assertEqual(pm2_list[0]['pm_id'], 0)
        self.assertEqual(pm2_list[0]['status'], 'online')
        self.assertEqual(pm2_list[1]['name'], 'another-api')
        self.assertEqual(pm2_list[1]['status'], 'stopped')

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_get_pm2_list_file_not_found_error(self, mock_print, mock_subprocess_run):
        mock_subprocess_run.side_effect = FileNotFoundError("pm2 not found")
        result = get_pm2_list()
        self.assertEqual(result, [])
        mock_print.assert_called_once_with("錯誤：PM2 命令未找到。請確認 PM2 已全局安裝。")

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_get_pm2_list_called_process_error(self, mock_print, mock_subprocess_run):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, ["pm2", "jlist"], stderr="PM2 command failed")
        result = get_pm2_list()
        self.assertEqual(result, [])
        mock_print.assert_called_once_with("錯誤：執行 PM2 命令失敗。錯誤訊息：PM2 command failed")

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_get_pm2_list_json_decode_error(self, mock_print, mock_subprocess_run):
        mock_subprocess_run.return_value = MagicMock(stdout="invalid json")
        result = get_pm2_list()
        self.assertEqual(result, [])
        mock_print.assert_called_once_with("錯誤：無法解析 PM2 輸出的 JSON 數據。")

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_get_pm2_list_unknown_error(self, mock_print, mock_subprocess_run):
        mock_subprocess_run.side_effect = Exception("some unexpected error")
        result = get_pm2_list()
        self.assertEqual(result, [])
        mock_print.assert_called_once_with("發生未知錯誤：some unexpected error")

    @patch('subprocess.run')
    def test_start_api_success(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = ""
        mock_subprocess_run.return_value.stderr = ""
        result_name = start_api("test-api-name")
        mock_subprocess_run.assert_any_call(["pm2", "start", "test-api-name"], capture_output=True, text=True, check=True)
        self.assertTrue(result_name)
        mock_subprocess_run.reset_mock()
        result_id = start_api(123)
        mock_subprocess_run.assert_any_call(["pm2", "start", "123"], capture_output=True, text=True, check=True)
        self.assertTrue(result_id)

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_start_api_file_not_found(self, mock_print, mock_subprocess_run):
        mock_subprocess_run.side_effect = FileNotFoundError("pm2 not found")
        result = start_api("nonexistent-api")
        self.assertFalse(result)
        mock_print.assert_called_with("錯誤：PM2 命令未找到。請確認 PM2 已全局安裝。")

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_start_api_called_process_error(self, mock_print, mock_subprocess_run):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "pm2 start", stderr="API already running")
        result = start_api("running-api")
        self.assertFalse(result)
        mock_print.assert_called_with("錯誤：啟動 API running-api 失敗。錯誤訊息：API already running")

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_start_api_unknown_error(self, mock_print, mock_subprocess_run):
        mock_subprocess_run.side_effect = Exception("some unexpected error")
        result = start_api("error-api")
        self.assertFalse(result)
        mock_print.assert_called_with("啟動 API error-api 時發生未知錯誤：some unexpected error")

    @patch('subprocess.run')
    def test_restart_api_success(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = ""
        mock_subprocess_run.return_value.stderr = ""
        result_name = restart_api("test-api-name")
        mock_subprocess_run.assert_any_call(["pm2", "restart", "test-api-name"], capture_output=True, text=True, check=True)
        self.assertTrue(result_name)
        mock_subprocess_run.reset_mock()
        result_id = restart_api(123)
        mock_subprocess_run.assert_any_call(["pm2", "restart", "123"], capture_output=True, text=True, check=True)
        self.assertTrue(result_id)

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_restart_api_file_not_found(self, mock_print, mock_subprocess_run):
        mock_subprocess_run.side_effect = FileNotFoundError("pm2 not found")
        result = restart_api("nonexistent-api")
        self.assertFalse(result)
        mock_print.assert_called_with("錯誤：PM2 命令未找到。請確認 PM2 已全局安裝。")

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_restart_api_called_process_error(self, mock_print, mock_subprocess_run):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "pm2 restart", stderr="API restart failed")
        result = restart_api("failed-api")
        self.assertFalse(result)
        mock_print.assert_called_with("錯誤：重啟 API failed-api 失敗。錯誤訊息：API restart failed")

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_restart_api_unknown_error(self, mock_print, mock_subprocess_run):
        mock_subprocess_run.side_effect = Exception("some unexpected error")
        result = restart_api("error-api")
        self.assertFalse(result)
        mock_print.assert_called_with("重啟 API error-api 時發生未知錯誤：some unexpected error")

    @patch('subprocess.run')
    def test_stop_api_success(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 0
        mock_subprocess_run.return_value.stdout = ""
        mock_subprocess_run.return_value.stderr = ""
        result_name = stop_api("test-api-name")
        mock_subprocess_run.assert_any_call(["pm2", "stop", "test-api-name"], capture_output=True, text=True, check=True)
        self.assertTrue(result_name)
        mock_subprocess_run.reset_mock()
        result_id = stop_api(123)
        mock_subprocess_run.assert_any_call(["pm2", "stop", "123"], capture_output=True, text=True, check=True)
        self.assertTrue(result_id)

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_stop_api_file_not_found(self, mock_print, mock_subprocess_run):
        mock_subprocess_run.side_effect = FileNotFoundError("pm2 not found")
        result = stop_api("nonexistent-api")
        self.assertFalse(result)
        mock_print.assert_called_with("錯誤：PM2 命令未找到。請確認 PM2 已全局安裝。")

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_stop_api_called_process_error(self, mock_print, mock_subprocess_run):
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "pm2 stop", stderr="API stop failed")
        result = stop_api("failed-api")
        self.assertFalse(result)
        mock_print.assert_called_with("錯誤：停止 API failed-api 失敗。錯誤訊息：API stop failed")

    @patch('subprocess.run')
    @patch('builtins.print')
    def test_stop_api_unknown_error(self, mock_print, mock_subprocess_run):
        mock_subprocess_run.side_effect = Exception("some unexpected error")
        result = stop_api("error-api")
        self.assertFalse(result)
        mock_print.assert_called_with("停止 API error-api 時發生未知錯誤：some unexpected error")

    @patch('src.pm2_manager.get_pm2_list')
    @patch('src.pm2_manager.start_api')
    @patch('builtins.print')
    def test_start_project_apis_success(self, mock_print, mock_start_api, mock_get_pm2_list):
        mock_get_pm2_list.return_value = [
            {'name': 'api-projA-1', 'pm_id': 100, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_A'}},
            {'name': 'api-projA-2', 'pm_id': 101, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_A'}},
            {'name': 'api-projB-1', 'pm_id': 200, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_B'}},
        ]
        mock_start_api.return_value = True

        result = start_project_apis("project_A")

        self.assertTrue(result)
        mock_start_api.assert_any_call(100)
        mock_start_api.assert_any_call(101)
        mock_print.assert_any_call("嘗試啟動專案 'project_A' 中的 API: api-projA-1 (ID: 100)")
        mock_print.assert_any_call("嘗試啟動專案 'project_A' 中的 API: api-projA-2 (ID: 101)")

    @patch('src.pm2_manager.get_pm2_list')
    @patch('src.pm2_manager.start_api')
    @patch('builtins.print')
    def test_start_project_apis_no_apis_found(self, mock_print, mock_start_api, mock_get_pm2_list):
        mock_get_pm2_list.return_value = [
            {'name': 'api-projB-1', 'pm_id': 200, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_B'}},
        ]

        result = start_project_apis("project_A")

        self.assertFalse(result)
        mock_start_api.assert_not_called()
        mock_print.assert_called_with("未找到專案 'project_A' 下的任何 API 服務。")

    @patch('src.pm2_manager.get_pm2_list')
    @patch('src.pm2_manager.start_api')
    @patch('builtins.print')
    def test_start_project_apis_partial_failure(self, mock_print, mock_start_api, mock_get_pm2_list):
        mock_get_pm2_list.return_value = [
            {'name': 'api-projA-1', 'pm_id': 100, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_A'}},
            {'name': 'api-projA-2', 'pm_id': 101, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_A'}},
        ]
        mock_start_api.side_effect = [True, False]

        result = start_project_apis("project_A")

        self.assertFalse(result)
        mock_start_api.assert_any_call(100)
        mock_start_api.assert_any_call(101)
        mock_print.assert_any_call("啟動 API: api-projA-2 (ID: 101) 失敗。")

    @patch('src.pm2_manager.get_pm2_list')
    @patch('src.pm2_manager.restart_api')
    @patch('builtins.print')
    def test_restart_project_apis_success(self, mock_print, mock_restart_api, mock_get_pm2_list):
        mock_get_pm2_list.return_value = [
            {'name': 'api-projA-1', 'pm_id': 100, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_A'}},
            {'name': 'api-projA-2', 'pm_id': 101, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_A'}},
            {'name': 'api-projB-1', 'pm_id': 200, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_B'}},
        ]
        mock_restart_api.return_value = True

        result = restart_project_apis("project_A")

        self.assertTrue(result)
        mock_restart_api.assert_any_call(100)
        mock_restart_api.assert_any_call(101)
        mock_print.assert_any_call("嘗試重啟專案 'project_A' 中的 API: api-projA-1 (ID: 100)")
        mock_print.assert_any_call("嘗試重啟專案 'project_A' 中的 API: api-projA-2 (ID: 101)")

    @patch('src.pm2_manager.get_pm2_list')
    @patch('src.pm2_manager.restart_api')
    @patch('builtins.print')
    def test_restart_project_apis_no_apis_found(self, mock_print, mock_restart_api, mock_get_pm2_list):
        mock_get_pm2_list.return_value = [
            {'name': 'api-projB-1', 'pm_id': 200, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_B'}},
        ]

        result = restart_project_apis("project_A")

        self.assertFalse(result)
        mock_restart_api.assert_not_called()
        mock_print.assert_called_with("未找到專案 'project_A' 下的任何 API 服務。")

    @patch('src.pm2_manager.get_pm2_list')
    @patch('src.pm2_manager.restart_api')
    @patch('builtins.print')
    def test_restart_project_apis_partial_failure(self, mock_print, mock_restart_api, mock_get_pm2_list):
        mock_get_pm2_list.return_value = [
            {'name': 'api-projA-1', 'pm_id': 100, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_A'}},
            {'name': 'api-projA-2', 'pm_id': 101, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_A'}},
        ]
        mock_restart_api.side_effect = [True, False]

        result = restart_project_apis("project_A")

        self.assertFalse(result)
        mock_restart_api.assert_any_call(100)
        mock_restart_api.assert_any_call(101)
        mock_print.assert_any_call("重啟 API: api-projA-2 (ID: 101) 失敗。")

    @patch('src.pm2_manager.get_pm2_list')
    @patch('src.pm2_manager.stop_api')
    @patch('builtins.print')
    def test_stop_project_apis_success(self, mock_print, mock_stop_api, mock_get_pm2_list):
        mock_get_pm2_list.return_value = [
            {'name': 'api-projA-1', 'pm_id': 100, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_A'}},
            {'name': 'api-projA-2', 'pm_id': 101, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_A'}},
            {'name': 'api-projB-1', 'pm_id': 200, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_B'}},
        ]
        mock_stop_api.return_value = True

        result = stop_project_apis("project_A")

        self.assertTrue(result)
        mock_stop_api.assert_any_call(100)
        mock_stop_api.assert_any_call(101)
        mock_print.assert_any_call("嘗試停止專案 'project_A' 中的 API: api-projA-1 (ID: 100)")
        mock_print.assert_any_call("嘗試停止專案 'project_A' 中的 API: api-projA-2 (ID: 101)")

    @patch('src.pm2_manager.get_pm2_list')
    @patch('src.pm2_manager.stop_api')
    @patch('builtins.print')
    def test_stop_project_apis_no_apis_found(self, mock_print, mock_stop_api, mock_get_pm2_list):
        mock_get_pm2_list.return_value = [
            {'name': 'api-projB-1', 'pm_id': 200, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_B'}},
        ]

        result = stop_project_apis("project_A")

        self.assertFalse(result)
        mock_stop_api.assert_not_called()
        mock_print.assert_called_with("未找到專案 'project_A' 下的任何 API 服務。")

    @patch('src.pm2_manager.get_pm2_list')
    @patch('src.pm2_manager.stop_api')
    @patch('builtins.print')
    def test_stop_project_apis_partial_failure(self, mock_print, mock_stop_api, mock_get_pm2_list):
        mock_get_pm2_list.return_value = [
            {'name': 'api-projA-1', 'pm_id': 100, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_A'}},
            {'name': 'api-projA-2', 'pm_id': 101, 'pm2_env': {'pm_cwd': '/Users/gamepig/projects/API_Manager/project_A'}},
        ]
        mock_stop_api.side_effect = [True, False]

        result = stop_project_apis("project_A")

        self.assertFalse(result)
        mock_stop_api.assert_any_call(100)
        mock_stop_api.assert_any_call(101)
        mock_print.assert_any_call("停止 API: api-projA-2 (ID: 101) 失敗。")

if __name__ == '__main__':
    unittest.main() 