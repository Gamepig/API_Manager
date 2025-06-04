import unittest
from PyQt6.QtWidgets import QApplication, QTableWidget, QHeaderView
from PyQt6.QtCore import Qt
from src.gui_components import ApiStatusLight, ApiDetailPanel, PerformanceGraph, ApiDataTable

app = QApplication([]) # Initialize QApplication once for all tests

class TestApiStatusLight(unittest.TestCase):

    def test_status_colors(self):
        # Test online status (green)
        light_online = ApiStatusLight("online")
        self.assertEqual(light_online.get_status(), "online")
        # For color testing, we can only check internal state or force a repaint
        # Actual visual verification might require manual inspection or more advanced GUI testing tools
        
        # Test stopped status (red)
        light_stopped = ApiStatusLight("stopped")
        self.assertEqual(light_stopped.get_status(), "stopped")

        # Test errored status (yellow)
        light_errored = ApiStatusLight("errored")
        self.assertEqual(light_errored.get_status(), "errored")

        # Test unknown status (gray)
        light_unknown = ApiStatusLight("unknown")
        self.assertEqual(light_unknown.get_status(), "unknown")

        # Test unstable status (yellow)
        light_unstable = ApiStatusLight("unstable")
        self.assertEqual(light_unstable.get_status(), "unstable")

    def test_set_status(self):
        light = ApiStatusLight("stopped")
        self.assertEqual(light.get_status(), "stopped")
        light.set_status("online")
        self.assertEqual(light.get_status(), "online")
        light.set_status("errored")
        self.assertEqual(light.get_status(), "errored")


class TestApiDetailPanel(unittest.TestCase):

    def setUp(self):
        self.mock_refresh_callback = unittest.mock.Mock()
        self.panel = ApiDetailPanel(refresh_callback=self.mock_refresh_callback)

    def test_update_detail(self):
        api_data = {
            "name": "test-api-1",
            "pm_id": 1,
            "status": "online",
            "cpu": 0.5,
            "memory": 100.0,
            "restarts": 5,
            "uptime": "1h 30m",
            "log_file_path": "/var/log/test-api-1.log",
            "project_path": "/home/user/projects/test-project",
            "metadata": {
                "description": "A test API for detail panel.",
                "version": "1.0.0",
                "maintainer": "Test User",
                "last_change": "2023-01-01"
            }
        }
        self.panel.update_detail(api_data)

        # Verify some labels are updated correctly
        self.assertIn("名稱: test-api-1", self.panel.info_labels["name"].text())
        self.assertIn("PM ID: 1", self.panel.info_labels["pm_id"].text())
        self.assertIn("狀態: online", self.panel.info_labels["status"].text())
        self.assertIn("描述: A test API for detail panel.", self.panel.info_labels["metadata.description"].text())
        self.assertEqual(self.panel.current_api_id, 1)

    def test_clear_detail(self):
        # First, update with some data
        api_data = {"name": "test-api", "pm_id": 1, "status": "online"}
        self.panel.update_detail(api_data)
        self.assertIsNotNone(self.panel.current_api_id)

        self.panel.clear_detail()
        # Verify labels are reset
        self.assertIn("名稱: N/A", self.panel.info_labels["name"].text())
        self.assertIn("PM ID: N/A", self.panel.info_labels["pm_id"].text())
        self.assertIn("狀態: N/A", self.panel.info_labels["status"].text())
        self.assertIsNone(self.panel.current_api_id)

    # Test button click events
    @unittest.mock.patch('src.pm2_manager.start_api')
    @unittest.mock.patch('PyQt6.QtWidgets.QMessageBox.information')
    @unittest.mock.patch('PyQt6.QtWidgets.QMessageBox.critical')
    def test_start_api_button(self, mock_critical, mock_information, mock_start_api):
        api_data = {"name": "test-api", "pm_id": 1, "status": "stopped"}
        self.panel.update_detail(api_data)

        mock_start_api.return_value = True
        self.panel.start_button.click()
        mock_start_api.assert_called_once_with(1)
        mock_information.assert_called_once()
        self.panel.refresh_callback.assert_called_once()

        mock_start_api.reset_mock()
        mock_information.reset_mock()
        self.panel.refresh_callback.reset_mock()

        mock_start_api.return_value = False
        self.panel.start_button.click()
        mock_start_api.assert_called_once_with(1)
        mock_critical.assert_called_once()
        self.panel.refresh_callback.assert_called_once()

    @unittest.mock.patch('src.pm2_manager.restart_api')
    @unittest.mock.patch('PyQt6.QtWidgets.QMessageBox.information')
    @unittest.mock.patch('PyQt6.QtWidgets.QMessageBox.critical')
    def test_restart_api_button(self, mock_critical, mock_information, mock_restart_api):
        api_data = {"name": "test-api", "pm_id": 1, "status": "online"}
        self.panel.update_detail(api_data)

        mock_restart_api.return_value = True
        self.panel.restart_button.click()
        mock_restart_api.assert_called_once_with(1)
        mock_information.assert_called_once()
        self.panel.refresh_callback.assert_called_once()

        mock_restart_api.reset_mock()
        mock_information.reset_mock()
        self.panel.refresh_callback.reset_mock()

        mock_restart_api.return_value = False
        self.panel.restart_button.click()
        mock_restart_api.assert_called_once_with(1)
        mock_critical.assert_called_once()
        self.panel.refresh_callback.assert_called_once()

    @unittest.mock.patch('src.pm2_manager.stop_api')
    @unittest.mock.patch('PyQt6.QtWidgets.QMessageBox.information')
    @unittest.mock.patch('PyQt6.QtWidgets.QMessageBox.critical')
    def test_stop_api_button(self, mock_critical, mock_information, mock_stop_api):
        api_data = {"name": "test-api", "pm_id": 1, "status": "online"}
        self.panel.update_detail(api_data)

        mock_stop_api.return_value = True
        self.panel.stop_button.click()
        mock_stop_api.assert_called_once_with(1)
        mock_information.assert_called_once()
        self.panel.refresh_callback.assert_called_once()

        mock_stop_api.reset_mock()
        mock_information.reset_mock()
        self.panel.refresh_callback.reset_mock()

        mock_stop_api.return_value = False
        self.panel.stop_button.click()
        mock_stop_api.assert_called_once_with(1)
        mock_critical.assert_called_once()
        self.panel.refresh_callback.assert_called_once()

    @unittest.mock.patch('PyQt6.QtWidgets.QMessageBox.warning')
    def test_control_buttons_no_api_selected(self, mock_warning):
        self.panel.clear_detail() # Ensure no API is selected

        self.panel.start_button.click()
        mock_warning.assert_called_once_with(self.panel, "未選擇 API", "請先從列表中選擇一個 API。")
        mock_warning.reset_mock()

        self.panel.restart_button.click()
        mock_warning.assert_called_once_with(self.panel, "未選擇 API", "請先從列表中選擇一個 API。")
        mock_warning.reset_mock()

        self.panel.stop_button.click()
        mock_warning.assert_called_once_with(self.panel, "未選擇 API", "請先從列表中選擇一個 API。")
        mock_warning.reset_mock()


class TestPerformanceGraph(unittest.TestCase):

    def setUp(self):
        self.graph = PerformanceGraph()
        # Mock the matplotlib drawing methods to avoid actual GUI rendering during tests
        self.graph.ax.clear = unittest.mock.Mock()
        self.graph.ax.plot = unittest.mock.Mock()
        self.graph.ax.set_title = unittest.mock.Mock()
        self.graph.ax.set_xlabel = unittest.mock.Mock()
        self.graph.ax.set_ylabel = unittest.mock.Mock()
        self.graph.ax.legend = unittest.mock.Mock()
        self.graph.ax.tick_params = unittest.mock.Mock()
        self.graph.figure.tight_layout = unittest.mock.Mock()
        self.graph.canvas.draw = unittest.mock.Mock()
        self.graph.timer.stop() # Stop the QTimer for predictable testing

    def test_plot_graph(self):
        self.graph.cpu_data = [10, 20, 30]
        self.graph.memory_data = [100, 200, 300]
        self.graph.time_data = ["10:00", "10:01", "10:02"]
        
        self.graph.plot_graph()

        self.graph.ax.clear.assert_called_once() # Verify clear is called
        self.assertEqual(self.graph.ax.plot.call_count, 2) # Called once for CPU, once for Memory
        self.graph.ax.plot.assert_any_call(self.graph.time_data, self.graph.cpu_data, label='CPU (%)', color='blue')
        self.graph.ax.plot.assert_any_call(self.graph.time_data, self.graph.memory_data, label='Memory (MB)', color='red')
        self.graph.ax.set_title.assert_called_once_with("CPU & Memory Usage")
        self.graph.ax.set_xlabel.assert_called_once_with("Time")
        self.graph.ax.set_ylabel.assert_called_once_with("Usage")
        self.graph.ax.legend.assert_called_once()
        self.graph.ax.tick_params.assert_called_once_with(axis='x', rotation=45)
        self.graph.figure.tight_layout.assert_called_once()
        self.graph.canvas.draw.assert_called_once()

    def test_clear_graph(self):
        self.graph.cpu_data = [10, 20, 30]
        self.graph.memory_data = [100, 200, 300]
        self.graph.time_data = ["10:00", "10:01", "10:02"]
        
        self.graph.clear_graph()

        self.assertEqual(len(self.graph.cpu_data), 0)
        self.assertEqual(len(self.graph.memory_data), 0)
        self.assertEqual(len(self.graph.time_data), 0)
        self.graph.ax.clear.assert_called_once()
        self.graph.ax.set_title.assert_called_once_with("CPU & Memory Usage")
        self.graph.ax.set_xlabel.assert_called_once_with("Time")
        self.graph.ax.set_ylabel.assert_called_once_with("Percentage / Bytes")
        self.graph.canvas.draw.assert_called_once()

    def test_update_graph_data(self):
        # Test with provided data
        self.graph.update_graph_data(cpu_value=50, memory_value=250)
        self.assertEqual(len(self.graph.cpu_data), 1)
        self.assertEqual(self.graph.cpu_data[0], 50)
        self.assertEqual(len(self.graph.memory_data), 1)
        self.assertEqual(self.graph.memory_data[0], 250)
        self.assertEqual(len(self.graph.time_data), 1)
        self.graph.ax.plot.assert_called() # plot_graph is called internally

        # Test max_points limit
        self.graph.cpu_data = [i for i in range(self.graph.max_points)]
        self.graph.memory_data = [i * 10 for i in range(self.graph.max_points)]
        self.graph.time_data = [str(i) for i in range(self.graph.max_points)]

        self.graph.update_graph_data(cpu_value=99, memory_value=999)
        self.assertEqual(len(self.graph.cpu_data), self.graph.max_points)
        self.assertEqual(self.graph.cpu_data[-1], 99)
        self.assertEqual(self.graph.memory_data[-1], 999)
        self.assertEqual(self.graph.cpu_data[0], 1) # First element should be removed


class TestApiDataTable(unittest.TestCase):

    def setUp(self):
        self.table = ApiDataTable()

    def test_update_table(self):
        api_data_list = [
            {"name": "api-a", "pm_id": 1, "status": "online", "project_name": "ProjectX"},
            {"name": "api-b", "pm_id": 2, "status": "stopped", "project_name": "ProjectY"},
            {"name": "api-c", "pm_id": 3, "status": "errored", "project_name": "ProjectX"},
        ]
        self.table.update_table(api_data_list)

        self.assertEqual(self.table.rowCount(), 3)
        self.assertEqual(self.table.columnCount(), 3)

        # Verify row 0
        self.assertEqual(self.table.item(0, 0).text(), "api-a")
        self.assertEqual(self.table.item(0, 1).text(), "ProjectX")
        self.assertIsInstance(self.table.cellWidget(0, 2), ApiStatusLight)
        self.assertEqual(self.table.cellWidget(0, 2).get_status(), "online")
        self.assertEqual(self.table.item(0, 0).data(Qt.ItemDataRole.UserRole)["pm_id"], 1)

        # Verify row 1
        self.assertEqual(self.table.item(1, 0).text(), "api-b")
        self.assertEqual(self.table.item(1, 1).text(), "ProjectY")
        self.assertIsInstance(self.table.cellWidget(1, 2), ApiStatusLight)
        self.assertEqual(self.table.cellWidget(1, 2).get_status(), "stopped")
        self.assertEqual(self.table.item(1, 0).data(Qt.ItemDataRole.UserRole)["pm_id"], 2)

        # Verify row 2
        self.assertEqual(self.table.item(2, 0).text(), "api-c")
        self.assertEqual(self.table.item(2, 1).text(), "ProjectX")
        self.assertIsInstance(self.table.cellWidget(2, 2), ApiStatusLight)
        self.assertEqual(self.table.cellWidget(2, 2).get_status(), "errored")
        self.assertEqual(self.table.item(2, 0).data(Qt.ItemDataRole.UserRole)["pm_id"], 3)

    def test_update_table_empty_list(self):
        self.table.update_table([])
        self.assertEqual(self.table.rowCount(), 0)

    def test_selection_behavior(self):
        self.assertEqual(self.table.selectionBehavior(), QTableWidget.SelectionBehavior.SelectRows)
        self.assertEqual(self.table.selectionMode(), QTableWidget.SelectionMode.SingleSelection)

    def test_header_visibility_and_resize_mode(self):
        self.assertFalse(self.table.verticalHeader().isVisible())
        self.assertEqual(self.table.horizontalHeader().sectionResizeMode(0), QHeaderView.ResizeMode.Stretch)


if __name__ == '__main__':
    unittest.main() 