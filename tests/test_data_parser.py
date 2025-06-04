"""
test_data_parser.py

此模組包含 `data_parser.py` 的單元測試。
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
import sys
from datetime import datetime, timedelta

# 將專案根目錄添加到 sys.path，以便找到 src 模組
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_parser import parse_pm2_list_output, get_project_name, load_api_metadata
from src.config import API_METADATA_FILENAME, API_METADATA_DIRNAME

class TestDataParser(unittest.TestCase):

    @patch('src.data_parser.load_api_metadata')
    def test_parse_pm2_list_output_success(self, mock_load_api_metadata):
        mock_load_api_metadata.return_value = {"api-name": {"version": "1.0.0"}}

        mock_pm2_output = """
        [
            {
                "name": "api-name",
                "pm_id": 0,
                "monit": {"cpu": 0, "memory": 1024},
                "restart_time": 5,
                "unstable_restarts": 1,
                "pm_uptime": 1678886400000,
                "pm2_env": {
                    "status": "online",
                    "pm_out_log_path": "/var/log/api-name.log",
                    "PWD": "/path/to/project/api-project",
                    "script": "/path/to/project/api-project/app.js"
                }
            }
        ]
        """
        # Mock datetime.now() to ensure consistent uptime calculation
        with patch('src.data_parser.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.fromtimestamp(1678886400000 / 1000 + 3600) # 1 hour later
            mock_datetime.fromtimestamp.return_value = datetime.fromtimestamp(1678886400000 / 1000)
            mock_datetime.timedelta = timedelta # ensure timedelta is not mocked

            parsed_data = parse_pm2_list_output(mock_pm2_output)

            self.assertEqual(len(parsed_data), 1)
            api = parsed_data[0]
            self.assertEqual(api['name'], 'api-name')
            self.assertEqual(api['pm_id'], 0)
            self.assertEqual(api['status'], 'online')
            self.assertEqual(api['cpu'], 0)
            self.assertEqual(api['memory'], 1024)
            self.assertEqual(api['restarts'], 5)
            self.assertEqual(api['uptime'], '1h')
            self.assertEqual(api['log_file_path'], '/var/log/api-name.log')
            self.assertEqual(api['project_path'], '/path/to/project/api-project')
            self.assertEqual(api['metadata'], {"version": "1.0.0"})

    def test_parse_pm2_list_output_empty_input(self):
        parsed_data = parse_pm2_list_output("[]")
        self.assertEqual(len(parsed_data), 0)

    @patch('builtins.print')
    def test_parse_pm2_list_output_invalid_json(self, mock_print):
        parsed_data = parse_pm2_list_output("invalid json")
        self.assertEqual(len(parsed_data), 0)
        mock_print.assert_called_with("錯誤：無法解析 PM2 輸出的 JSON 數據。")

    @patch('builtins.print')
    def test_parse_pm2_list_output_missing_keys(self, mock_print):
        mock_pm2_output = """
        [
            {
                "missing_name_key": 0,
                "monit": {},
                "pm2_env": {}
            }
        ]
        """
        # Mock datetime.now() for consistency even if uptime is not calculated
        with patch('src.data_parser.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.fromtimestamp(0)
            mock_datetime.fromtimestamp.return_value = datetime.fromtimestamp(0)
            mock_datetime.timedelta = timedelta
            parsed_data = parse_pm2_list_output(mock_pm2_output)
            self.assertEqual(len(parsed_data), 1)
            api = parsed_data[0]
            self.assertIsNone(api['name'])
            self.assertEqual(api['status'], 'unknown')
            self.assertEqual(api['cpu'], 0)
            self.assertEqual(api['memory'], 0)
            self.assertEqual(api['restarts'], 0)
            self.assertEqual(api['uptime'], 'N/A')
            self.assertEqual(api['log_file_path'], 'N/A')
            self.assertEqual(api['project_path'], 'N/A')
            self.assertEqual(api['metadata'], {})
        mock_print.assert_not_called() # No error should be printed for missing optional keys

    def test_get_project_name_from_path(self):
        api_data = {"project_path": "/home/user/projects/my_project"}
        self.assertEqual(get_project_name(api_data, {}), "my_project")

    def test_get_project_name_empty_path(self):
        api_data = {"project_path": ""}
        self.assertEqual(get_project_name(api_data, {}), "Unknown Project")

    def test_get_project_name_n_a_path(self):
        api_data = {"project_path": "N/A"}
        self.assertEqual(get_project_name(api_data, {}), "Unknown Project")

    def test_get_project_name_root_path(self):
        api_data = {"project_path": "/"}
        self.assertEqual(get_project_name(api_data, {}), "/")

    def test_get_project_name_with_trailing_slash(self):
        api_data = {"project_path": "/home/user/projects/my_project/"}
        self.assertEqual(get_project_name(api_data, {}), "my_project")

    @patch('builtins.open', new_callable=mock_open, read_data='{"api-name": {"version": "1.0.0"}}')
    @patch('os.path.exists', return_value=True)
    def test_load_api_metadata_success(self, mock_exists, mock_file):
        metadata = load_api_metadata("/path/to/project")
        self.assertEqual(metadata, {"api-name": {"version": "1.0.0"}})
        mock_exists.assert_called_with("/path/to/project/docs/api.json")
        mock_file.assert_called_with("/path/to/project/docs/api.json", 'r', encoding='utf-8')

    @patch('builtins.print')
    @patch('os.path.exists', return_value=False)
    def test_load_api_metadata_file_not_found(self, mock_exists, mock_print):
        metadata = load_api_metadata("/path/to/nonexistent_project")
        self.assertEqual(metadata, {})
        mock_print.assert_called_with("警告：未找到專案 '/path/to/nonexistent_project' 的 api.json 檔案於 /path/to/nonexistent_project/docs/api.json")

    @patch('builtins.open', new_callable=mock_open, read_data='invalid json')
    @patch('os.path.exists', return_value=True)
    @patch('builtins.print')
    def test_load_api_metadata_invalid_json(self, mock_print, mock_exists, mock_file):
        metadata = load_api_metadata("/path/to/project")
        self.assertEqual(metadata, {})
        mock_print.assert_called_with("錯誤：無法解析 /path/to/project/docs/api.json 的 JSON 數據。")

    @patch('builtins.open', side_effect=Exception("permission denied"))
    @patch('os.path.exists', return_value=True)
    @patch('builtins.print')
    def test_load_api_metadata_unknown_error(self, mock_print, mock_exists, mock_file):
        metadata = load_api_metadata("/path/to/project")
        self.assertEqual(metadata, {})
        mock_print.assert_called_with("讀取 /path/to/project/docs/api.json 時發生未知錯誤：permission denied")

    def test_load_api_metadata_empty_project_path(self):
        metadata = load_api_metadata("")
        self.assertEqual(metadata, {})

    def test_load_api_metadata_n_a_project_path(self):
        metadata = load_api_metadata("N/A")
        self.assertEqual(metadata, {})

if __name__ == '__main__':
    unittest.main() 