# Light theme stylesheet
LIGHT_STYLE = """
QMainWindow, QDialog {
    background-color: #f0f0f0;
    color: #202020;
}
QTableWidget {
    background-color: white;
    alternate-background-color: #f9f9f9;
    color: black;
    selection-background-color: #d0d0d0;
    selection-color: black;
}
QHeaderView::section {
    background-color: #e0e0e0;
    color: #505050;
    border: 1px solid #c0c0c0;
}
QLabel, QStatusBar {
    color: #202020;
}
QMenuBar {
    background-color: #f0f0f0;
    color: #202020;
}
QMenuBar::item {
    background-color: transparent;
    color: #202020;
}
QMenuBar::item:selected {
    background-color: #d0d0d0;
}
QMenu {
    background-color: #f0f0f0;
    color: #202020;
}
QMenu::item:selected {
    background-color: #d0d0d0;
}
QPushButton {
    background-color: #e0e0e0;
    color: #202020;
    border: 1px solid #c0c0c0;
    border-radius: 3px;
    padding: 5px;
}
QPushButton:hover {
    background-color: #d0d0d0;
}
QPushButton:pressed {
    background-color: #c0c0c0;
}
QLineEdit {
    background-color: white;
    color: #202020;
    border: 1px solid #c0c0c0;
    border-radius: 3px;
    padding: 3px;
}
"""

# Dark theme stylesheet
DARK_STYLE = """
QMainWindow, QDialog {
    background-color: #2d2d2d;
    color: #e0e0e0;
}
QTableWidget {
    background-color: #3c3c3c;
    alternate-background-color: #353535;
    color: #e0e0e0;
    gridline-color: #5a5a5a;
    selection-background-color: #45657a;
    selection-color: white;
}
QHeaderView::section {
    background-color: #2a2a2a;
    color: #e0e0e0;
    border: 1px solid #5a5a5a;
}
QLabel, QStatusBar {
    color: #e0e0e0;
}
QMenuBar {
    background-color: #2d2d2d;
    color: #e0e0e0;
}
QMenuBar::item {
    background-color: transparent;
    color: #e0e0e0;
}
QMenuBar::item:selected {
    background-color: #404040;
}
QMenu {
    background-color: #2d2d2d;
    color: #e0e0e0;
}
QMenu::item:selected {
    background-color: #404040;
}
QPushButton {
    background-color: #404040;
    color: #e0e0e0;
    border: 1px solid #5a5a5a;
    border-radius: 3px;
    padding: 5px;
}
QPushButton:hover {
    background-color: #505050;
}
QPushButton:pressed {
    background-color: #606060;
}
QLineEdit {
    background-color: #3c3c3c;
    color: #e0e0e0;
    border: 1px solid #5a5a5a;
    border-radius: 3px;
    padding: 3px;
}
QStatusBar {
    background-color: #2a2a2a;
    color: #e0e0e0;
}
"""