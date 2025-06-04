import unittest
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from datetime import datetime
import unittest.mock # 導入 unittest.mock

# 將專案根目錄添加到 Python 路徑中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main_app import MainApp
from src import pm2_manager
from src.data_parser import parse_pm2_list_output, get_project_name

# 為了測試，我們可能需要模擬 pm2 命令的輸出。
# 這裡先建立一個基本的框架，後續會加入詳細的測試用例。

class TestIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # 確保 QApplication 只有一個實例
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
        cls.window = MainApp()
        cls.window.show()
        QTest.qWaitForWindowExposed(cls.window) # 等待視窗顯示

    @classmethod
    def tearDownClass(cls):
        cls.window.close()
        cls.app.quit()

    def setUp(self):
        # 每次測試前重置應用程式狀態
        self.window.load_api_data() # 重新載入數據，確保測試環境一致
        QTest.qWait(1000) # 給予一些時間讓數據載入和 UI 更新

    def test_gui_displays_api_list(self):
        """
        測試 GUI 是否能正確顯示來自 PM2 的 API 列表。
        """
        # 假設我們有一些模擬的 PM2 數據
        mock_pm2_output = [
            {
                "name": "dummy-api-project",
                "pm_id": 0,
                "pm2_env": {"status": "online", "created_at": datetime.now().timestamp() * 1000, "pm_cwd": "/path/to/project/dummy-api-project"},
                "monit": {"cpu": 1.0, "memory": 1024 * 1024 * 10}
            },
            {
                "name": "another-api",
                "pm_id": 1,
                "pm2_env": {"status": "stopped", "created_at": (datetime.now().timestamp() - 3600) * 1000, "pm_cwd": "/path/to/project/another-project"},
                "monit": {"cpu": 0.0, "memory": 0}
            }
        ]

        # 模擬 pm2_manager.get_pm2_list 返回這些數據
        original_get_pm2_list = pm2_manager.get_pm2_list
        pm2_manager.get_pm2_list = lambda: mock_pm2_output
        
        self.window.load_api_data() # 強制更新數據
        QTest.qWait(500) # 給予時間更新 UI

        # 驗證樹狀圖中是否有項目
        root = self.window.api_list_widget.invisibleRootItem()
        self.assertGreater(root.childCount(), 0, "樹狀圖中應該有專案項目")

        # 驗證特定 API 是否存在
        found_dummy_api = False
        found_another_api = False
        for i in range(root.childCount()):
            project_item = root.child(i)
            for j in range(project_item.childCount()):
                api_item = project_item.child(j)
                if api_item.text(0) == "dummy-api-project":
                    found_dummy_api = True
                if api_item.text(0) == "another-api":
                    found_another_api = True
        
        self.assertTrue(found_dummy_api, "應找到 dummy-api-project")
        self.assertTrue(found_another_api, "應找到 another-api")

        # 恢復原來的函數
        pm2_manager.get_pm2_list = original_get_pm2_list

    def test_api_control_buttons(self):
        """
        測試啟動、重啟、停止按鈕是否能正確觸發後端功能。
        需要模擬 pm2_manager 的啟動/重啟/停止函數。
        """
        # 假設樹狀圖中已經有 API，我們選取第一個 API 進行測試
        self.window.load_api_data()
        QTest.qWait(1000)

        root = self.window.api_list_widget.invisibleRootItem()
        if root.childCount() > 0:
            project_item = root.child(0)
            if project_item.childCount() > 0:
                api_item = project_item.child(0)
                self.window.api_list_widget.setCurrentItem(api_item) # 選取第一個 API
                self.window.display_api_details(api_item) # 顯示其詳細資訊
                QTest.qWait(500)

                # 模擬 pm2_manager 的控制函數
                mock_start = unittest.mock.Mock(return_value=True)
                mock_restart = unittest.mock.Mock(return_value=True)
                mock_stop = unittest.mock.Mock(return_value=True)

                with unittest.mock.patch('src.pm2_manager.start_api', mock_start):
                    with unittest.mock.patch('src.pm2_manager.restart_api', mock_restart):
                        with unittest.mock.patch('src.pm2_manager.stop_api', mock_stop):
                            # 點擊啟動按鈕
                            self.window.api_detail_panel.start_button.click()
                            QTest.qWait(200) # 給予時間處理點擊事件
                            mock_start.assert_called_once() # 驗證啟動函數被調用
                            mock_start.reset_mock()

                            # 點擊重啟按鈕
                            self.window.api_detail_panel.restart_button.click()
                            QTest.qWait(200)
                            mock_restart.assert_called_once()
                            mock_restart.reset_mock()

                            # 點擊停止按鈕
                            self.window.api_detail_panel.stop_button.click()
                            QTest.qWait(200)
                            mock_stop.assert_called_once()
                            mock_stop.reset_mock()
            else:
                self.skipTest("沒有 API 子項目可供測試控制按鈕")
        else:
            self.skipTest("沒有專案可供測試控制按鈕")

if __name__ == '__main__':
    # 需要先初始化 QApplication 才能運行 Qt 相關測試
    app = QApplication(sys.argv)
    unittest.main()
    sys.exit(app.exec_()) 