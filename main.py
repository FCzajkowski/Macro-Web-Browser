import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QLabel, QHBoxLayout, QLineEdit, QTabWidget, QListWidget, QListWidgetItem
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

class CustomBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #FFFFFF;")  # Set main white background

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Left Panel
        self.left_panel = QVBoxLayout()
        self.left_panel_widget = QWidget()
        self.left_panel_widget.setFixedWidth(200)
        self.left_panel_widget.setStyleSheet("background-color: white;")
        self.left_panel_widget.setLayout(self.left_panel)

        # Logo at the Top
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        icon = QIcon("logo.png")
        pixmap = icon.pixmap(100, 100)
        self.logo_label.setPixmap(pixmap)
        self.left_panel.addWidget(self.logo_label)

        # URL Input Field
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter website URL")
        self.url_input.setStyleSheet("padding: 10px; border: 1px solid lightgray;")
        self.url_input.returnPressed.connect(self.load_url)
        self.left_panel.addWidget(self.url_input)

        # New Tab Button
        self.new_tab_button = QPushButton("+ NEW TAB")
        self.new_tab_button.setStyleSheet("background-color: white; border: none; color: gray;")
        self.new_tab_button.clicked.connect(lambda: self.add_new_tab("https://www.google.com"))
        self.left_panel.addWidget(self.new_tab_button)

        # Tabs List Under the Button
        self.tab_list = QListWidget()
        self.tab_list.setStyleSheet("background-color: #f2f2f2; border: none; padding: 10px;")
        self.tab_list.clicked.connect(self.switch_tab_from_list)
        self.left_panel.addWidget(self.tab_list)

        # Add left panel to layout
        self.layout.addWidget(self.left_panel_widget)

        # Browser area without visible tabs on top
        self.browser_container = QVBoxLayout()
        self.browser_widget = QWidget()
        self.browser_widget.setLayout(self.browser_container)
        self.layout.addWidget(self.browser_widget)

        # Hidden Tab Management
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_tab_list)
        self.tabs.setStyleSheet("QTabBar::tab { display: none; }")  # Hide tabs completely

        self.browser_container.addWidget(self.tabs)

        # Load tabs from JSON
        self.tabs_file = "tabs.json"
        self.load_tabs_from_file()

    def add_new_tab(self, url="https://www.google.com"):
        # Create a new browser view
        new_browser = QWebEngineView()
        new_browser.setUrl(QUrl(url))
        new_browser.titleChanged.connect(self.update_tab_title)

        # Add to tabs
        tab_index = self.tabs.addTab(new_browser, "New Tab")
        self.tabs.setCurrentIndex(tab_index)
        self.update_tab_list()

    def load_url(self):
        url = self.url_input.text()
        if url:
            if not url.startswith("http"):
                url = "https://" + url
            current_browser = self.tabs.currentWidget()
            if isinstance(current_browser, QWebEngineView):
                current_browser.setUrl(QUrl(url))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
            self.update_tab_list()

    def update_tab_title(self):
        current_browser = self.tabs.currentWidget()
        if isinstance(current_browser, QWebEngineView):
            title = current_browser.title() or "New Tab"
            self.tabs.setTabText(self.tabs.currentIndex(), title)
            self.update_tab_list()

    def update_tab_list(self):
        self.tab_list.clear()
        for i in range(self.tabs.count()):
            self.tab_list.addItem(self.tabs.tabText(i))

    def switch_tab_from_list(self):
        current_row = self.tab_list.currentRow()
        if current_row >= 0:
            self.tabs.setCurrentIndex(current_row)

    def save_tabs_to_file(self):
        tabs_data = []
        for i in range(self.tabs.count()):
            browser = self.tabs.widget(i)
            if isinstance(browser, QWebEngineView):
                tabs_data.append(browser.url().toString())
        with open(self.tabs_file, "w") as file:
            json.dump(tabs_data, file)

    def load_tabs_from_file(self):
        try:
            with open(self.tabs_file, "r") as file:
                tabs_data = json.load(file)
            if not tabs_data:
                self.add_new_tab()  # If file is empty, load a default tab
            for url in tabs_data:
                self.add_new_tab(url)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file does not exist or is corrupted, add a default tab
            self.add_new_tab()

    def closeEvent(self, event):
        self.save_tabs_to_file()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Improve styling for high-DPI displays
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(255, 255, 255))  # Match the white background
    app.setPalette(palette)

    # Set application logo
    app.setWindowIcon(QIcon("logo.png"))

    window = CustomBrowser()
    window.show()
    sys.exit(app.exec_())
