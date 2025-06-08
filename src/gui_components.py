"""
gui_components.py

此模組包含 PM2 API 管理應用中可重複使用的 GUI 組件，例如狀態燈、API 列表表格、詳細資訊面板和性能圖表。
"""

import matplotlib
matplotlib.use('QtAgg')  # 確保 Matplotlib 使用 PyQt6 後端
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel, QWidget, QTableWidget, QVBoxLayout, QHBoxLayout, QHeaderView,
    QTableWidgetItem, QMessageBox, QPushButton
)

from src import pm2_manager


class ApiStatusLight(QWidget):
    """
    一個小部件，根據 API 狀態顯示不同顏色的圓點和狀態文字。

    Attributes:
        _status (str): 當前 API 的狀態 (e.g., "online", "stopped", "errored").
        layout (QHBoxLayout): 用於佈局圓點和狀態文字的佈局管理器。
        color_circle (QLabel): 顯示狀態圓點的 QLabel。
        status_label (QLabel): 顯示狀態文字的 QLabel。
    """
    def __init__(self, status="unknown", parent=None):
        """
        初始化 ApiStatusLight 小部件。

        Args:
            status (str): 初始 API 狀態，默認為 "unknown"。
            parent (QWidget, optional): 父小部件。默認為 None。
        """
        super().__init__(parent)
        self._status = status
        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)  # 設置圓點和文字之間的間距

        self.color_circle = QLabel()
        self.color_circle.setFixedSize(16, 16)
        self.color_circle.setStyleSheet("""
            border-radius: 8px;
            background-color: gray;
            border: 1px solid #555;
        """)

        self.status_label = QLabel(self._status)
        self.status_label.setStyleSheet("color: #F0F0F0; font-weight: bold;")
        self.status_label.setContentsMargins(0, 0, 0, 0)
        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.layout.addWidget(self.color_circle)
        self.layout.addWidget(self.status_label)
        self.layout.addStretch(1)

        self.update_color_and_text()

    def set_status(self, status: str):
        """
        設置 API 的狀態並更新圓點顏色和文字。

        Args:
            status (str): 新的 API 狀態。
        """
        if self._status != status:
            self._status = status
            self.update_color_and_text()

    def get_status(self) -> str:
        """
        獲取當前 API 的狀態。

        Returns:
            str: 當前 API 的狀態。
        """
        return self._status

    def update_color_and_text(self):
        """
        根據當前狀態更新圓點的顏色和狀態文字。
        """
        color_name = "gray"
        text_color = "#F0F0F0"
        if self._status == "online":
            color_name = "#28a745"  # Green
        elif self._status == "stopped":
            color_name = "#dc3545"  # Red
        elif self._status == "errored" or self._status == "unstable":
            color_name = "#ffc107"  # Yellow

        self.color_circle.setStyleSheet(f"""
            border-radius: 8px;
            background-color: {color_name};
            border: 1px solid {color_name};
        """)
        self.status_label.setText(self._status)
        self.status_label.setStyleSheet(
            f"color: {text_color}; font-weight: bold;")

    def sizeHint(self) -> QSize:
        """
        返回小部件的推薦大小。

        Returns:
            QSize: 推薦的大小 (80, 20)。
        """
        return QSize(80, 20)  # 調整大小以適應文字和圓點


class ApiDataTable(QTableWidget):
    """
    用於顯示 API 列表的表格組件。

    Attributes:
        None
    """
    def __init__(self, parent=None):
        """
        初始化 ApiDataTable。

        Args:
            parent (QWidget, optional): 父小部件。默認為 None。
        """
        super().__init__(parent)
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["API 名稱", "專案", "狀態"])
        self.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)  # 整行選取
        self.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection)  # 單行選取
        self.verticalHeader().setVisible(False)  # 隱藏垂直表頭
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)  # 自動拉伸列寬

    def update_table(self, api_data_list: list):
        """
        更新表格內容。

        Args:
            api_data_list (list): 包含 API 數據字典的列表。
        """
        self.setRowCount(len(api_data_list))
        for row, api_data in enumerate(api_data_list):
            name_item = QTableWidgetItem(api_data.get("name", "N/A"))
            project_name = api_data.get("project_name", "Unknown Project")
            project_item = QTableWidgetItem(project_name)

            status_light = ApiStatusLight(api_data.get("status", "unknown"))

            self.setItem(row, 0, name_item)
            self.setItem(row, 1, project_item)
            self.setCellWidget(row, 2, status_light)

            # 將完整的 api_data 存儲在 item 的 user data 中，方便後續點擊時獲取
            name_item.setData(Qt.ItemDataRole.UserRole, api_data)


class ApiDetailPanel(QWidget):
    """
    顯示單個 API 詳細資訊的面板。

    Attributes:
        layout (QVBoxLayout): 面板的主佈局管理器。
        info_labels (dict): 儲存各資訊標籤的字典。
        current_api_id (str): 當前顯示的 API 的 PM2 ID。
        current_api_name (str): 當前顯示的 API 的名稱。
        refresh_callback (callable): 用於刷新應用程式數據的回調函數。
        labels_data (dict): 定義顯示文本和對應 API 數據鍵路徑的字典。
        start_button (QPushButton): 啟動 API 按鈕。
        restart_button (QPushButton): 重啟 API 按鈕。
        stop_button (QPushButton): 停止 API 按鈕。
    """
    single_api_action_requested = pyqtSignal(object, str, str, str) # action_func, api_id, api_name, action_type

    def __init__(self, parent=None, refresh_callback=None):
        """
        初始化 ApiDetailPanel。

        Args:
            parent (QWidget, optional): 父小部件。默認為 None。
            refresh_callback (callable, optional): 用於刷新應用程式數據的回調函數。默認為 None。
        """
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.info_labels = {}
        self.current_api_id = None  # Store the pm_id of the currently displayed API
        self.current_api_name = None # Store the name of the currently displayed API
        self.refresh_callback = refresh_callback  # Store the callback function
        self.labels_data = {
            "名稱": "name",
            "PM ID": "pm_id",
            "狀態": "status",
            "CPU": "cpu",
            "記憶體": "memory",
            "重啟次數": "restarts",
            "運行時間": "uptime",
            "日誌路徑": "log_file_path",
            "專案路徑": "project_path",
            "端口": "port",
            "基本功能描述": "metadata.description",
            "版本": "metadata.version",
            "維護者": "metadata.maintainer",
            "上次變更": "metadata.last_change"
        }
        self.setup_ui()

    def setup_ui(self):
        """
        設置面板的 UI 元素，包括資訊標籤和控制按鈕。
        """
        for display_text, key_path in self.labels_data.items():
            label = QLabel(f"{display_text}: N/A")
            self.layout.addWidget(label)
            self.info_labels[key_path] = label

        # Add control buttons
        control_buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("啟動")
        self.restart_button = QPushButton("重啟")
        self.stop_button = QPushButton("停止")

        control_buttons_layout.addWidget(self.start_button)
        control_buttons_layout.addWidget(self.restart_button)
        control_buttons_layout.addWidget(self.stop_button)
        self.layout.addLayout(control_buttons_layout)

        self.layout.addStretch(1)

        # Connect buttons
        self.start_button.clicked.connect(self._start_api)
        self.restart_button.clicked.connect(self._restart_api)
        self.stop_button.clicked.connect(self._stop_api)

    def update_detail(self, api_data: dict):
        """
        根據提供的 API 數據更新面板上顯示的詳細資訊。

        Args:
            api_data (dict): 包含單個 API 詳細資訊的字典。
        """
        self.clear_detail()
        if not api_data:
            self.current_api_id = None
            self.current_api_name = None
            return

        self.current_api_id = api_data.get('pm_id')  # Store the current API ID
        self.current_api_name = api_data.get('name') # Store the current API name

        # Use labels_data to iterate
        for display_text, key_path in self.labels_data.items():
            label = self.info_labels[key_path]
            value = api_data
            # Traverse nested keys if any (e.g., "metadata.description")
            for key in key_path.split('.'):
                if isinstance(value, dict):
                    value = value.get(key, "N/A")
                else:
                    value = "N/A"
                    break
            label.setText(f"{display_text}: {value}")

    def clear_detail(self):
        """
        清除面板上顯示的所有 API 詳細資訊，並將其重置為 "N/A"。
        """
        self.current_api_id = None
        self.current_api_name = None
        for display_text, key_path in self.labels_data.items():
            label = self.info_labels[key_path]
            label.setText(f"{display_text}: N/A")

    def _start_api(self):
        """
        處理啟動 API 按鈕的點擊事件。
        發射信號以在獨立線程中啟動 API。
        """
        if self.current_api_id is not None:
            print(f"DEBUG: ApiDetailPanel._start_api - ID: {self.current_api_id}, Name: {self.current_api_name}") # 診斷用
            QMessageBox.information(self, "啟動 API",
                                    f"正在啟動 API: {self.current_api_name} (ID: {self.current_api_id})")
            self.single_api_action_requested.emit(pm2_manager.start_api, str(self.current_api_id), self.current_api_name, "啟動")

    def _restart_api(self):
        """
        處理重啟 API 按鈕的點擊事件。
        發射信號以在獨立線程中重啟 API。
        """
        if self.current_api_id is not None:
            print(f"DEBUG: ApiDetailPanel._restart_api - ID: {self.current_api_id}, Name: {self.current_api_name}") # 診斷用
            QMessageBox.information(self, "重啟 API",
                                    f"正在重啟 API: {self.current_api_name} (ID: {self.current_api_id})")
            self.single_api_action_requested.emit(pm2_manager.restart_api, str(self.current_api_id), self.current_api_name, "重啟")

    def _stop_api(self):
        """
        處理停止 API 按鈕的點擊事件。
        發射信號以在獨立線程中停止 API。
        """
        if self.current_api_id is not None:
            print(f"DEBUG: ApiDetailPanel._stop_api - ID: {self.current_api_id}, Name: {self.current_api_name}") # 診斷用
            QMessageBox.information(self, "停止 API",
                                    f"正在停止 API: {self.current_api_name} (ID: {self.current_api_id})")
            self.single_api_action_requested.emit(pm2_manager.stop_api, str(self.current_api_id), self.current_api_name, "停止")


class PerformanceGraph(QWidget):
    """
    顯示 CPU 和記憶體使用率的圓餅圖。

    Attributes:
        figure (matplotlib.figure.Figure): Matplotlib 圖形對象。
        canvas (matplotlib.backends.backend_qtagg.FigureCanvasQTAgg):
            圖形繪製區域。
        ax (matplotlib.axes.Axes): 圖形的軸對象。
        cpu_series (QPieSeries): CPU 使用率圓餅圖系列。
        mem_label (QLabel): 顯示記憶體使用率的文字標籤。
    """
    def __init__(self, parent=None):
        """
        初始化 PerformanceGraph。

        Args:
            parent (QWidget, optional): 父小部件。默認為 None。
        """
        super().__init__(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect('equal')  # 確保圓餅圖是圓的
        self.ax.set_title('CPU/Memory Usage', color='white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')

        # 記憶體文字顯示
        self.mem_label = QLabel("Memory: N/A")
        self.mem_label.setStyleSheet("color: #F0F0F0; font-weight: bold;")
        self.mem_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.mem_label)

        self.cpu_series = None
        self.clear_graph()

    def plot_graph(self, cpu_usage=0, memory_usage=0):
        """
        繪製 CPU 使用率圓餅圖並顯示記憶體使用率。

        Args:
            cpu_usage (float): CPU 使用率 (0-100)。
            memory_usage (int): 記憶體使用率 (Bytes)。
        """
        self.ax.clear()

        # CPU 圓餅圖
        cpu_remaining = 100 - cpu_usage
        sizes = [cpu_usage, cpu_remaining]
        labels = ['CPU', '']
        colors = ['#28a745', '#555']  # Green for CPU, Gray for remaining

        self.cpu_series = self.ax.pie(sizes, labels=labels, colors=colors,
                                      startangle=90, counterclock=False,
                                      wedgeprops=dict(width=0.3, edgecolor='w'))
        self.ax.text(0, 0, f'{cpu_usage:.1f}%', ha='center', va='center',
                     fontsize=14, color='white')

        # 記憶體文字顯示
        mem_gb = memory_usage / (1024**3)  # 轉換為 GB
        self.mem_label.setText(f"Memory: {mem_gb:.2f} GB")

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def clear_graph(self):
        """
        清除圖表和記憶體顯示。
        """
        self.ax.clear()
        self.ax.set_title('CPU/Memory Usage', color='white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.set_aspect('equal')
        self.ax.text(0, 0, 'N/A', ha='center', va='center',
                     fontsize=14, color='white')
        self.mem_label.setText("Memory: N/A")
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def sizeHint(self) -> QSize:
        """
        返回小部件的推薦大小。

        Returns:
            QSize: 推薦的大小 (200, 250)。
        """
        return QSize(200, 250)


class LoadingOverlay(QWidget):
    """
    一個半透明的覆蓋層，用於在後台操作時顯示載入訊息。

    Attributes:
        message_label (QLabel): 顯示載入訊息的標籤。
    """
    def __init__(self, parent=None):
        """
        初始化 LoadingOverlay。

        Args:
            parent (QWidget, optional): 父小部件。默認為 None。
        """
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        layout = QVBoxLayout(self)
        self.message_label = QLabel("載入中...")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
        """)
        layout.addWidget(self.message_label)
        self.setLayout(layout)

    def resizeEvent(self, event):
        """
        處理小部件大小調整事件，確保覆蓋層始終與父小部件大小一致。

        Args:
            event (QResizeEvent): 大小調整事件。
        """
        if self.parentWidget():
            self.setGeometry(self.parentWidget().rect())
        super().resizeEvent(event)

    def set_message(self, message: str):
        """
        設置載入訊息。

        Args:
            message (str): 要顯示的訊息。
        """
        self.message_label.setText(message)

    def show_overlay(self):
        """
        顯示覆蓋層。
        """
        if self.parentWidget():
            self.raise_()
            self.showFullScreen()

    def hide_overlay(self):
        """
        隱藏覆蓋層。
        """
        self.hide() 