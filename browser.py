import sys
import json
import concurrent.futures
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLineEdit, QAction, 
    QToolBar, QFileDialog, QMessageBox, QPushButton, QProgressBar, QStyleFactory, 
    QLabel, QHBoxLayout, QTabBar, QMenu
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QKeySequence


# Signal to update the bookmark menu from a background thread
class UpdateBookmarkMenuSignal(QObject):
    update_menu = pyqtSignal(list)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Enhanced QTWebEngine Browser")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize bookmarks list and dark mode state
        self.bookmarks = []
        self.is_dark_mode = False
        self.is_fullscreen = False

        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create the tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tabs)

        # Create the navigation bar
        self.nav_bar = QToolBar("Navigation")
        self.addToolBar(self.nav_bar)

        # Back and forward buttons
        back_btn = QAction("Back", self)
        back_btn.setStatusTip("Back")
        back_btn.setShortcut(QKeySequence.Back)
        back_btn.triggered.connect(self.back)
        self.nav_bar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.setStatusTip("Forward")
        forward_btn.setShortcut(QKeySequence.Forward)
        forward_btn.triggered.connect(self.forward)
        self.nav_bar.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.setStatusTip("Reload")
        reload_btn.setShortcut(QKeySequence.Refresh)
        reload_btn.triggered.connect(self.reload)
        self.nav_bar.addAction(reload_btn)

        new_tab_btn = QAction("New Tab", self)
        new_tab_btn.setStatusTip("New Tab")
        new_tab_btn.triggered.connect(self.add_new_tab)
        self.nav_bar.addAction(new_tab_btn)

        # Address bar and search button
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.navigate_to_url_from_bar)
        self.nav_bar.addWidget(self.address_bar)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.navigate_to_url_from_bar)
        self.nav_bar.addWidget(search_btn)

        # Fullscreen button
        fullscreen_btn = QAction("Fullscreen", self)
        fullscreen_btn.setStatusTip("Toggle Fullscreen Mode")
        fullscreen_btn.triggered.connect(self.toggle_fullscreen)
        self.nav_bar.addAction(fullscreen_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(10)
        layout.addWidget(self.progress_bar)

        # Bookmark actions
        bookmark_btn = QAction("Bookmark", self)
        bookmark_btn.setStatusTip("Bookmark This Page")
        bookmark_btn.triggered.connect(self.add_bookmark)
        self.nav_bar.addAction(bookmark_btn)

        # Mode toggle button
        self.mode_toggle_btn = QAction("Switch to Dark Mode", self)
        self.mode_toggle_btn.setStatusTip("Toggle Dark/Light Mode")
        self.mode_toggle_btn.triggered.connect(self.toggle_dark_mode)
        self.nav_bar.addAction(self.mode_toggle_btn)

        # Menu Bar
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("File")

        # Load bookmarks from file
        load_action = QAction("Load Bookmarks", self)
        load_action.setStatusTip("Load bookmarks from file")
        load_action.triggered.connect(self.load_bookmarks)
        file_menu.addAction(load_action)

        # Save bookmarks to file
        save_action = QAction("Save Bookmarks", self)
        save_action.setStatusTip("Save bookmarks to file")
        save_action.triggered.connect(self.save_bookmarks)
        file_menu.addAction(save_action)

        # Exit application
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Bookmarks menu
        self.bookmark_menu = QMenu("Bookmarks", self)
        self.menu_bar.addMenu(self.bookmark_menu)
        self.bookmark_menu.aboutToShow.connect(self.update_bookmark_menu)

        # Set the initial URL
        self.add_new_tab()
        self.navigate_to_url("http://www.google.com")

        # Create a signal instance for updating the bookmark menu
        self.update_menu_signal = UpdateBookmarkMenuSignal()
        self.update_menu_signal.update_menu.connect(self.update_bookmark_menu_from_signal)

        # Create a thread pool executor
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    def apply_dark_mode(self):
        dark_mode_qss = """
        /* Dark mode styles */
        """
        self.setStyleSheet(dark_mode_qss)

    def apply_light_mode(self):
        light_mode_qss = """
        /* Light mode styles */
        """
        self.setStyleSheet(light_mode_qss)

    def toggle_dark_mode(self):
        if self.is_dark_mode:
            self.apply_light_mode()
            self.mode_toggle_btn.setText("Switch to Dark Mode")
        else:
            self.apply_dark_mode()
            self.mode_toggle_btn.setText("Switch to Light Mode")
        self.is_dark_mode = not self.is_dark_mode

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
            self.fullscreen_btn.setText("Fullscreen")
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText("Exit Fullscreen")
        self.is_fullscreen = not self.is_fullscreen

    def add_new_tab(self, url="http://www.google.com"):
        if not isinstance(url, str):
            url = "http://www.google.com"  # Fallback to a default URL if not a string

        tab = QWidget()
        layout = QVBoxLayout(tab)
    
        # Initialize the browser
        browser = QWebEngineView()
    
        # Set the URL
        browser.setUrl(QUrl.fromUserInput(url))

        # Connect signals
        browser.titleChanged.connect(lambda title: self.update_tab_title(tab, title))
        browser.loadStarted.connect(self.on_load_started)
        browser.loadProgress.connect(self.on_load_progress)
        browser.loadFinished.connect(self.on_load_finished)
    
        layout.addWidget(browser)
        tab.setLayout(layout)
    
        # Add the new tab
        index = self.tabs.addTab(tab, "New Tab")
    
        # Create a custom tab with a close button
        custom_tab = QWidget()
        custom_tab_layout = QHBoxLayout(custom_tab)
        custom_tab_layout.setContentsMargins(0, 0, 0, 0)
        title_label = QLabel("New Tab")
        custom_tab_layout.addWidget(title_label)
        close_button = QPushButton("✕")
        close_button.setMaximumSize(16, 16)
        close_button.clicked.connect(lambda: self.close_tab(index))
        custom_tab_layout.addWidget(close_button)
    
        # Set the custom tab widget
        self.tabs.tabBar().setTabButton(index, QTabBar.RightSide, custom_tab)
    
        self.tabs.setCurrentIndex(index)
        self.update_address_bar()  # Ensure this method is defined

    def update_address_bar(self):
        current_browser = self.current_browser()
        if current_browser:
            url = current_browser.url().toString()
            self.address_bar.setText(url)

    def update_tab_title(self, tab, title):
        index = self.tabs.indexOf(tab)
        if index != -1:
            custom_tab = self.tabs.tabBar().tabButton(index, QTabBar.RightSide)
            if custom_tab:
                title_label = custom_tab.findChild(QLabel, "")
                if title_label:
                    title_label.setText(title)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def navigate_to_url(self, url=None):
        if url is None:
            url = self.address_bar.text().strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        if not QUrl(url).isValid():
            QMessageBox.warning(self, "Invalid URL", "The URL you entered is invalid.")
            return
        current_browser = self.current_browser()
        if current_browser:
            current_browser.setUrl(QUrl(url))

    def navigate_to_url_from_bar(self):
        self.navigate_to_url()

    def back(self):
        current_browser = self.current_browser()
        if current_browser:
            current_browser.back()

    def forward(self):
        current_browser = self.current_browser()
        if current_browser:
            current_browser.forward()

    def reload(self):
        current_browser = self.current_browser()
        if current_browser:
            current_browser.reload()

    def add_bookmark(self):
        current_browser = self.current_browser()
        if current_browser:
            url = current_browser.url().toString()
            title = current_browser.title()
            if (url, title) not in self.bookmarks:
                self.bookmarks.append((url, title))
                self.update_bookmark_menu()

    def update_bookmark_menu_from_signal(self, bookmarks):
        self.bookmark_menu.clear()
        for url, title in bookmarks:
            bookmark_action = QAction(title, self)
            bookmark_action.setData(url)
            bookmark_action.triggered.connect(self.navigate_bookmark)
            self.bookmark_menu.addAction(bookmark_action)

    def update_bookmark_menu(self):
        # Offload the bookmark menu update to a background thread
        self.executor.submit(self.update_bookmark_menu_from_signal, self.bookmarks)

    def navigate_bookmark(self):
        action = self.sender()
        url = action.data()
        self.navigate_to_url(url)

    def load_bookmarks(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Bookmark File", "", "JSON Files (*.json)")
        if file_name:
            self.executor.submit(self._load_bookmarks_from_file, file_name)

    def _load_bookmarks_from_file(self, file_name):
        try:
            with open(file_name, "r") as file:
                bookmarks = json.load(file)
                self.bookmarks = bookmarks
                # Update the UI on the main thread
                QMetaObject.invokeMethod(self.update_bookmark_menu_from_signal, "update_menu", Qt.QueuedConnection, Q_ARG(list, self.bookmarks))
        except Exception as e:
            QMetaObject.invokeMethod(self, "critical_error", Qt.QueuedConnection, Q_ARG(str, f"Failed to load bookmarks: {e}"))

    def save_bookmarks(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Bookmark File", "", "JSON Files (*.json)")
        if file_name:
            self.executor.submit(self._save_bookmarks_to_file, file_name)

    def _save_bookmarks_to_file(self, file_name):
        try:
            with open(file_name, "w") as file:
                json.dump(self.bookmarks, file, indent=4)
        except Exception as e:
            QMetaObject.invokeMethod(self, "critical_error", Qt.QueuedConnection, Q_ARG(str, f"Failed to save bookmarks: {e}"))

    def current_browser(self):
        current_index = self.tabs.currentIndex()
        if current_index != -1:
            return self.tabs.widget(current_index).findChild(QWebEngineView, "")
        return None

    def on_load_started(self):
        self.progress_bar.setValue(0)
        self.progress_bar.show()

    def on_load_progress(self, progress):
        self.progress_bar.setValue(progress)

    def on_load_finished(self, success):
        if success:
            self.progress_bar.setValue(100)
        else:
            self.progress_bar.setValue(0)
        # Hide progress bar after loading is finished
        self.progress_bar.hide()

    def critical_error(self, message):
        QMessageBox.critical(self, "Error", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))  # Ensure consistent look
    browser = Browser()
    browser.show()
    sys.exit(app.exec_())
