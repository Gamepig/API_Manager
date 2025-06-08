"""
main_app.py

此模組負責構建 PM2 API 管理應用的主 GUI 介面，包括主視窗、整體佈局和核心交互邏輯。
"""

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, QMainWindow, QHeaderView, QAbstractItemView, QTreeWidgetItem, QTreeWidget, QMessageBox, QMenu
from PyQt6.QtCore import Qt, QTimer, QObject, QThread, pyqtSignal

# 為了讓應用程式能夠找到 src 目錄下的模組，將 src 目錄添加到 Python 路徑中
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 匯入後端模組
from src import pm2_manager
from src.data_parser import parse_pm2_list_output, get_project_name, load_all_api_configs
from src.gui_components import ApiStatusLight, ApiDetailPanel, PerformanceGraph, LoadingOverlay

# 載入 QSS 樣式表
def load_stylesheet(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""

class Worker(QObject):
    """
    獨立於主線程執行耗時操作的 Worker 物件。
    使用 QThread 將其移動到單獨的線程中，以避免阻塞 GUI。

    Signals:
        finished: 當任務完成時發出信號。
        error (str): 當任務中發生錯誤時，帶有錯誤訊息發出信號。
        data_loaded (list): 當 API 數據成功載入時，帶有解析後的 API 列表發出信號。
        action_completed (bool, int, int, str): 當專案操作完成時發出信號，包含成功狀態、成功計數、總計數和操作名稱。
        single_action_completed (bool, str, str, str): 用於單一 API 操作完成
    """
    finished = pyqtSignal()
    error = pyqtSignal(str)
    data_loaded = pyqtSignal(list)
    action_completed = pyqtSignal(bool, int, int, str)
    single_action_completed = pyqtSignal(bool, str, str, str)

    def __init__(self, parent=None):
        """
        初始化 Worker 物件。

        Args:
            parent (QObject, optional): 父物件。默認為 None。
        """
        super().__init__(parent)

    def load_data_task(self):
        """
        在單獨的線程中載入 PM2 API 數據。
        完成後發出 `data_loaded` 或 `error` 信號，最終發出 `finished` 信號。
        """
        try:
            raw_pm2_list = pm2_manager.get_pm2_list()
            if raw_pm2_list:
                parsed_apis = parse_pm2_list_output(raw_pm2_list)
                self.data_loaded.emit(parsed_apis)
            else:
                self.data_loaded.emit([]) # Emit empty list if no APIs found
        except Exception as e:
            self.error.emit(f"載入 API 數據時發生錯誤: {e}")
        finally:
            self.finished.emit()

    def perform_single_action_task(self, action_func, api_id, api_name, action_type):
        """
        在單獨的線程中執行單一 API 操作（啟動、重啟、停止）。

        Args:
            action_func (callable): 要執行的 PM2 管理函數。
            api_id (str): API 的 PM2 ID。
            api_name (str): API 的名稱。
            action_type (str): 操作類型 (e.g., "啟動", "停止", "重啟").
        """
        success = False
        message = ""
        try:
            success = action_func(api_id)
            message = "成功" if success else "失敗"
        except Exception as e:
            message = f"執行 {action_type} {api_name} 時發生錯誤: {e}"
            self.error.emit(message) # 也發出錯誤信號到主線程
        finally:
            self.single_action_completed.emit(success, api_name, action_type, message)
            self.finished.emit()

    def perform_action_task(self, action_func, action_name: str, project_names: set):
        """
        在單獨的線程中執行專案層級的 API 操作（啟動、重啟、停止）。

        Args:
            action_func (callable): 要執行的 PM2 管理函數 (e.g., `pm2_manager.start_project_apis`).
            action_name (str): 操作的名稱 (e.g., "啟動").
            project_names (set): 要執行操作的專案名稱集合。
        """
        success_count = 0
        total_count = 0
        try:
            # 在 worker 線程中載入 API 配置
            all_api_configs = load_all_api_configs()
            for project_name in sorted(list(project_names)):
                # Get the number of APIs in this project within the worker thread
                project_apis = [api for api in parse_pm2_list_output(pm2_manager.get_pm2_list()) if get_project_name(api, all_api_configs) == project_name]
                if project_apis:
                    total_count += len(project_apis)
                    if action_func(project_name):
                        success_count += len(project_apis) # Assuming success for all APIs in the project if the function returns True
            self.action_completed.emit(True, success_count, total_count, action_name)
        except Exception as e:
            self.error.emit(f"執行 {action_name} 專案 API 時發生錯誤: {e}")
            self.action_completed.emit(False, success_count, total_count, action_name) # Emit false on error
        finally:
            self.finished.emit()

class MainApp(QMainWindow):
    """
    PM2 API 管理應用程式的主視窗。

    Attributes:
        central_widget (QWidget): 應用程式的中央小部件。
        main_layout (QVBoxLayout): 主視窗的佈局管理器。
        loading_overlay (LoadingOverlay): 顯示加載動畫的覆蓋層。
        load_data_thread (QThread): 用於數據載入的獨立線程。
        load_data_worker (Worker): 執行數據載入任務的 Worker 物件。
        action_thread (QThread): 用於執行 API 操作的獨立線程。
        action_worker (Worker): 執行 API 操作任務的 Worker 物件。
        api_list_widget (QTreeWidget): 顯示 API 列表的樹狀部件。
        api_detail_panel (ApiDetailPanel): 顯示選定 API 詳細資訊的面板。
        performance_graph (PerformanceGraph): 顯示 CPU/記憶體使用率圖表的部件。
        _last_expanded_state (set): 儲存樹狀列表上次展開狀態的集合。
        _last_selected_item_data (dict): 儲存上次選取項目數據的字典。
        data_loading_in_progress (bool): 標記數據載入進度。
        data_ready_for_overlay_hide (bool): 新增旗標：數據是否已準備好隱藏疊加層
        min_overlay_display_timer (QTimer): 用於確保加載動畫至少顯示 1 秒的定時器
    """
    # 定義自定義信號
    load_data_signal = pyqtSignal()
    perform_action_signal = pyqtSignal(object, str, set) # action_func, action_name, project_names
    perform_single_action_signal = pyqtSignal(object, str, str, str) # action_func, api_id, api_name, action_type

    def __init__(self):
        """
        初始化 MainApp 主視窗。
        """
        super().__init__()
        self.setWindowTitle("PM2 API Manager")
        self.setGeometry(100, 100, 1200, 800) # x, y, width, height

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self._last_expanded_state = set() # 用於儲存樹狀列表的展開狀態
        self._last_selected_item_data = None # 用於儲存選取的項目數據
        # 初始化數據載入進度旗標
        self.data_loading_in_progress = False
        self.data_ready_for_overlay_hide = False # 新增旗標：數據是否已準備好隱藏疊加層

        self.init_ui()
        self.loading_overlay = LoadingOverlay(self) # 實例化 LoadingOverlay
        self.loading_overlay.hide() # 初始隱藏
        
        # 處理數據載入完成後的動作，即使數據載入速度非常快，也確保加載動畫至少顯示 1 秒
        self.min_overlay_display_timer = QTimer(self)
        self.min_overlay_display_timer.setInterval(1000) # 設置最小顯示時間為 1 秒
        self.min_overlay_display_timer.setSingleShot(True) # 設置為單次觸發
        self.min_overlay_display_timer.timeout.connect(self._check_and_hide_overlay)

        # 初始化 QThread 和 Worker，但不立即啟動
        self.load_data_thread = QThread()
        self.load_data_worker = Worker()
        self.load_data_worker.moveToThread(self.load_data_thread)
        self.load_data_worker.data_loaded.connect(self.update_api_tree_widget)
        self.load_data_worker.error.connect(self.handle_error)
        self.load_data_worker.finished.connect(self.load_api_data_finished)
        # 連接自定義信號到 worker 的任務方法
        self.load_data_signal.connect(self.load_data_worker.load_data_task)
        self.load_data_thread.start() # 啟動線程，但不執行任何任務

        self.action_thread = QThread()
        self.action_worker = Worker()
        self.action_worker.moveToThread(self.action_thread)
        self.action_worker.action_completed.connect(self.handle_action_completed)
        self.action_worker.error.connect(self.handle_error)
        self.action_worker.finished.connect(self._refresh_data_after_action) # 動作完成後刷新數據
        # 連接自定義信號到 worker 的任務方法
        self.perform_action_signal.connect(self.action_worker.perform_action_task)
        self.action_worker.single_action_completed.connect(self.handle_single_action_completed) # 連接單一 API 操作完成信號
        self.perform_single_action_signal.connect(self.action_worker.perform_single_action_task) # 連接單一 API 動作信號到 worker
        self.action_thread.start() # 啟動線程，但不執行任何任務

        self.load_api_data() # 首次載入數據
        self.setup_data_refresh_timer()

    def init_ui(self):
        """
        初始化主視窗的 UI 元素和佈局。
        """
        # Top section: Title and global control buttons
        top_layout = QHBoxLayout()
        title_label = QLabel("<h1>PM2 API Manager Dashboard</h1>")
        top_layout.addWidget(title_label)

        global_control_buttons_layout = QHBoxLayout()
        start_all_button = QPushButton("啟動所有")
        restart_all_button = QPushButton("重啟所有")
        stop_all_button = QPushButton("停止所有")

        global_control_buttons_layout.addWidget(start_all_button)
        global_control_buttons_layout.addWidget(restart_all_button)
        global_control_buttons_layout.addWidget(stop_all_button)
        top_layout.addLayout(global_control_buttons_layout)
        self.main_layout.addLayout(top_layout)

        # Connect global control buttons
        start_all_button.clicked.connect(self._start_all_projects)
        restart_all_button.clicked.connect(self._restart_all_projects)
        stop_all_button.clicked.connect(self._stop_all_projects)

        # Main content area: API list (left) and detail/graph (right)
        content_layout = QHBoxLayout()

        # Left: API list area
        self.api_list_widget = QTreeWidget()
        self.api_list_widget.setHeaderLabels(["API 名稱", "狀態"])
        self.api_list_widget.itemClicked.connect(self.display_api_details)
        self.api_list_widget.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # API 名稱列自動拉伸
        self.api_list_widget.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed) # 狀態列固定
        self.api_list_widget.setColumnWidth(1, 80)
        self.api_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu) # 啟用自定義上下文菜單
        self.api_list_widget.customContextMenuRequested.connect(self._show_context_menu) # 連接信號到槽
        content_layout.addWidget(self.api_list_widget, 2) #占 2/3 寬度

        # Right: API detail and graph display area
        right_panel_layout = QVBoxLayout()
        self.api_detail_panel = ApiDetailPanel(refresh_callback=self.load_api_data)
        # 連接 ApiDetailPanel 發出的單一 API 操作請求信號到 MainApp 的 perform_single_action_signal
        self.api_detail_panel.single_api_action_requested.connect(self.perform_single_action_signal)
        self.performance_graph = PerformanceGraph()
        right_panel_layout.addWidget(self.api_detail_panel)
        right_panel_layout.addWidget(self.performance_graph)
        content_layout.addLayout(right_panel_layout, 1) #占 1/3 寬度

        self.main_layout.addLayout(content_layout)

    def resizeEvent(self, event):
        """
        重寫 resizeEvent，確保加載覆蓋層與中央小部件的大小同步。

        Args:
            event (QResizeEvent): 調整大小事件。
        """
        super().resizeEvent(event)
        if self.loading_overlay:
            self.loading_overlay.setGeometry(self.central_widget.geometry())

    def load_api_data(self):
        """
        開始載入 API 數據，顯示加載動畫並在獨立線程中執行數據載入任務。
        """
        if self.data_loading_in_progress:
            print("數據載入已在進行中，跳過新的載入請求。")
            return

        print("載入 API 數據... (開始)")
        self.data_loading_in_progress = True
        self.loading_overlay.show_overlay()
        self.min_overlay_display_timer.start() # 開始計時，確保動畫至少顯示 1 秒
        # 通過信號觸發 worker 任務
        self.load_data_signal.emit()
        print("load_api_data: 觸發數據載入信號，data_loading_in_progress = True")

    def update_api_tree_widget(self, parsed_apis: list):
        """
        根據解析後的 API 數據更新 API 樹狀列表。
        會保留上次的展開狀態和選取狀態。

        Args:
            parsed_apis (list): 包含解析後 API 數據字典的列表。
        """
        # 儲存當前展開的項目和選取的項目
        expanded_items = set()
        selected_api_id = None # 儲存選取的 API ID，用於重新選取

        root = self.api_list_widget.invisibleRootItem()
        for i in range(root.childCount()):
            project_item = root.child(i)
            if project_item.isExpanded():
                expanded_items.add(project_item.text(0))
            
            # 檢查每個子項目是否被選取
            for j in range(project_item.childCount()):
                api_item = project_item.child(j)
                if api_item.isSelected():
                    api_data = api_item.data(0, Qt.ItemDataRole.UserRole)
                    if api_data and 'pm_id' in api_data: # 使用 pm_id 作為唯一識別碼
                        selected_api_id = api_data['pm_id']
                    break # 找到選取的項目後即可退出內層循環
            if selected_api_id is not None: # 如果找到選取的項目，退出外層循環
                break

        self.api_list_widget.clear()
        # Group APIs by project name
        projects = {}
        for api in parsed_apis:
            project_name = api.get('project_name', 'Unknown Project') # 直接從 api 字典中獲取 project_name
            if project_name not in projects:
                projects[project_name] = []
            projects[project_name].append(api)

        # Populate the tree widget
        for project_name, apis in sorted(projects.items()):
            project_item = QTreeWidgetItem([project_name, ""]) # 專案項目不顯示狀態
            project_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "project", "name": project_name}) # 標記為專案類型
            self.api_list_widget.addTopLevelItem(project_item)

            for api in sorted(apis, key=lambda x: x.get('name', '')):
                api_name = api.get("name", "N/A")
                status_light_widget = ApiStatusLight(api.get("status", "unknown"))
                
                api_item = QTreeWidgetItem([api_name, ""])
                api_item.setData(0, Qt.ItemDataRole.UserRole, api) # 將完整的 api_data 存儲在 item 的 user data 中
                project_item.addChild(api_item)
                self.api_list_widget.setItemWidget(api_item, 1, status_light_widget) # 將狀態燈號放置在第二列

                # 恢復展開狀態
                if project_name in expanded_items:
                    project_item.setExpanded(True)

                # 恢復選取狀態
                if selected_api_id is not None and api.get('pm_id') == selected_api_id:
                    self.api_list_widget.setCurrentItem(api_item) # 選取該項目
                    self.display_api_details(api_item) # 重新顯示詳細資訊

    def display_api_details(self, item: QTreeWidgetItem):
        """
        當用戶點擊 API 列表中的項目時，顯示該 API 的詳細資訊和性能圖表。

        Args:
            item (QTreeWidgetItem): 被點擊的樹狀列表項目。
        """
        api_data = item.data(0, Qt.ItemDataRole.UserRole)
        if api_data and api_data.get("type") != "project": # 確保是 API 項目而不是專案項目
            # if api_data.get("name") == "python-api":
            #     print("python-api") # 診斷用
            self._last_selected_item_data = api_data # 儲存選取的項目數據
            self.api_detail_panel.update_detail(api_data)
            cpu_usage = api_data.get("cpu", 0)
            memory_usage = api_data.get("memory", 0) # 確保這裡傳遞的是原始的位元組值
            self.performance_graph.plot_graph(cpu_usage, memory_usage)
        else:
            # 如果點擊的是專案，清空詳細面板
            self.api_detail_panel.clear_detail()
            self.performance_graph.clear_graph()
            self._last_selected_item_data = None # 如果選取了專案，則清空上次選取的 API 數據

    def _start_all_projects(self):
        """
        啟動所有專案中的所有 API 服務。
        """
        self._perform_project_action(pm2_manager.start_project_apis, "啟動所有 API")

    def _restart_all_projects(self):
        """
        重啟所有專案中的所有 API 服務。
        """
        self._perform_project_action(pm2_manager.restart_project_apis, "重啟所有 API")

    def _stop_all_projects(self):
        """
        停止所有專案中的所有 API 服務。
        """
        self._perform_project_action(pm2_manager.stop_project_apis, "停止所有 API")

    def _perform_project_action(self, action_func, action_name: str, target_projects: set = None):
        """
        執行一個通用的專案級別 API 操作。

        Args:
            action_func (callable): 要執行的 PM2 管理函數 (e.g., `pm2_manager.start_project_apis`).
            action_name (str): 操作的名稱 (e.g., "啟動").
            target_projects (set, optional): 要操作的專案名稱集合。如果為 None，則操作所有專案。默認為 None。
        """
        if target_projects is None:
            target_projects = pm2_manager.get_all_project_names() # Get all known project names
        
        if not target_projects:
            QMessageBox.information(self, "操作提示", f"沒有找到任何可執行的 API 服務來 {action_name}。")
            return

        self.loading_overlay.set_message(f"{action_name} 中...")
        self.loading_overlay.show_overlay()
        # 發射信號以在 worker 線程中執行動作
        self.perform_action_signal.emit(action_func, action_name, target_projects)

    def setup_data_refresh_timer(self):
        """
        設置一個定時器，定期刷新 API 數據。
        """
        print("setup_data_refresh_timer: 設置定時器")
        self.timer = QTimer(self)
        self.timer.setInterval(30000) # 將刷新間隔從 5 秒改為 30 秒
        self.timer.timeout.connect(self.load_api_data)
        self.timer.start() # 在這裡啟動定時器，並使其持續運行

    def handle_error(self, error_message: str):
        """
        處理在 Worker 線程中發生的錯誤並顯示錯誤訊息。

        Args:
            error_message (str): 錯誤訊息。
        """
        self.loading_overlay.hide_overlay()
        QMessageBox.critical(self, "錯誤", error_message)

    def handle_action_completed(self, success: bool, success_count: int, total_count: int, action_name: str):
        """
        處理專案 API 操作完成的結果，並顯示訊息框。

        Args:
            success (bool): 操作是否成功。
            success_count (int): 成功執行操作的 API 數量。
            total_count (int): 嘗試執行操作的 API 總數量。
            action_name (str): 執行操作的名稱 (e.g., "啟動所有 API")。
        """
        self.loading_overlay.hide_overlay()
        if success:
            if total_count > 0:
                QMessageBox.information(self, "操作成功", f"已成功 {action_name} {success_count} / {total_count} 個 API。")
            else:
                QMessageBox.information(self, "操作成功", f"沒有找到任何 API 來 {action_name}。")
        else:
            QMessageBox.critical(self, "操作失敗", f"{action_name} 失敗。成功 {success_count} / {total_count} 個 API。")

    def handle_single_action_completed(self, success: bool, api_name: str, action_type: str, message: str):
        """
        處理單一 API 操作完成的結果。

        Args:
            success (bool): 操作是否成功。
            api_name (str): 執行操作的 API 名稱。
            action_type (str): 操作類型 (e.g., "啟動", "停止", "重啟").
            message (str): 操作結果的訊息。
        """
        print(f"單一 API 操作完成 - {action_type} {api_name}: {message}")
        # 不在這裡直接呼叫 load_api_data，因為 _refresh_data_after_action 會處理

    def load_api_data_finished(self):
        """
        處理 API 數據載入完成的信號，隱藏加載動畫。
        """
        print("load_api_data_finished: 數據載入完成，隱藏 overlay，重置旗標")
        self.data_ready_for_overlay_hide = True # 數據已準備好隱藏疊加層
        self._check_and_hide_overlay() # 嘗試隱藏疊加層
        # 確保在數據載入完成後，如果之前有選取的項目，重新選取並顯示其詳細信息
        if self._last_selected_item_data:
            pm_id_to_select = self._last_selected_item_data.get('pm_id')
            if pm_id_to_select:
                root = self.api_list_widget.invisibleRootItem()
                for i in range(root.childCount()):
                    project_item = root.child(i)
                    for j in range(project_item.childCount()):
                        api_item = project_item.child(j)
                        api_data = api_item.data(0, Qt.ItemDataRole.UserRole)
                        if api_data and api_data.get('pm_id') == pm_id_to_select:
                            self.api_list_widget.setCurrentItem(api_item) # 選取該項目
                            self.display_api_details(api_item) # 重新顯示詳細資訊
                            break
                    if self.api_list_widget.currentItem(): # 如果已選取，則退出外層循環
                        break

    def _show_context_menu(self, point):
        """
        顯示 API 列表的上下文菜單（右鍵菜單）。

        Args:
            point (QPoint): 右鍵點擊的位置。
        """
        item = self.api_list_widget.itemAt(point)
        if item:
            menu = QMenu(self)
            api_data = item.data(0, Qt.ItemDataRole.UserRole)
            if api_data and api_data.get("type") == "project":
                # 專案層級的菜單
                project_name = api_data.get("name")
                start_project_action = menu.addAction(f"啟動 {project_name} 所有 API")
                stop_project_action = menu.addAction(f"停止 {project_name} 所有 API")
                restart_project_action = menu.addAction(f"重啟 {project_name} 所有 API")
                start_project_action.triggered.connect(lambda: self._start_selected_project_apis(project_name))
                stop_project_action.triggered.connect(lambda: self._stop_selected_project_apis(project_name))
                restart_project_action.triggered.connect(lambda: self._restart_selected_project_apis(project_name)) # 新增重啟
            else: # API item
                # 單一 API 層級的菜單
                api_id = api_data.get("pm_id") if api_data else None
                api_name = api_data.get("name") if api_data else "N/A"
                if api_id is not None:
                    start_action = menu.addAction(f"啟動 {api_name}")
                    restart_action = menu.addAction(f"重啟 {api_name}")
                    stop_action = menu.addAction(f"停止 {api_name}")
                    start_action.triggered.connect(lambda: self.perform_single_action_signal.emit(pm2_manager.start_api, str(api_id), api_name, "啟動"))
                    restart_action.triggered.connect(lambda: self.perform_single_action_signal.emit(pm2_manager.restart_api, str(api_id), api_name, "重啟"))
                    stop_action.triggered.connect(lambda: self.perform_single_action_signal.emit(pm2_manager.stop_api, str(api_id), api_name, "停止"))

            menu.exec(self.api_list_widget.mapToGlobal(point))

    def _stop_selected_project_apis(self, project_name: str):
        """
        停止選定專案中的所有 API 服務。

        Args:
            project_name (str): 要停止的專案名稱。
        """
        self._perform_project_action(pm2_manager.stop_project_apis, f"停止 {project_name} 的 API", {project_name})

    def _start_selected_project_apis(self, project_name: str):
        """
        啟動選定專案中的所有 API 服務。

        Args:
            project_name (str): 要啟動的專案名稱。
        """
        self._perform_project_action(pm2_manager.start_project_apis, f"啟動 {project_name} 的 API", {project_name})

    def _restart_selected_project_apis(self, project_name: str):
        """
        重啟選定專案中的所有 API 服務。

        Args:
            project_name (str): 要重啟的專案名稱。
        """
        self._perform_project_action(pm2_manager.restart_project_apis, f"重啟 {project_name} 的 API", {project_name})

    def _refresh_data_after_action(self):
        """
        處理動作完成後刷新數據的信號。
        """
        print("DEBUG: _refresh_data_after_action 觸發，正在重新載入數據...") # 診斷用
        self.load_api_data() # 重新載入數據

    def _check_and_hide_overlay(self):
        """
        檢查數據是否已載入完成，並在最小顯示時間過後隱藏加載動畫。
        """
        if self.data_ready_for_overlay_hide:
            self.loading_overlay.hide_overlay()
            self.data_loading_in_progress = False
            self.data_ready_for_overlay_hide = False

def main():
    """
    應用程式的入口點。創建 QApplication 實例並運行主應用程式。
    """
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet("style.qss")) # 載入 QSS 樣式表
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 