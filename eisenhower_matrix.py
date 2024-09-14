"""This module implements the Eisenhower Matrix GUI and integrates with Todoist API."""

import sys
from requests.exceptions import HTTPError
from todoist_api_python.api import TodoistAPI
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QListWidget,
    QErrorMessage,
)


class MainWindow(QWidget):
    """Main window for the Eisenhower Matrix application."""

    def __init__(self):
        """Initializes the main window with a grid of quadrants and a title."""
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.grid_layout = QGridLayout()

        self.ui_elements = {
            "labels": {},
            "list_widgets": {},
            "button_containers": {},
            "buttons": {},
            "line_edits": {},
        }

        self.quads = (
            "Urgent/Important",
            "Urgent/Unimportant",
            "Not Urgent/Important",
            "Not Urgent/ Not Important",
        )

        self.title = QLabel("Eisenhower Matrix")
        self.title.setAlignment(Qt.AlignHCenter)
        self.layout.addWidget(self.title)

        for i in range(2):
            for j in range(2):
                vbox = QVBoxLayout()

                # label = QLabel(f"Label {i*2 + j + 1}")
                label = QLabel(self.quads[i * 2 + j])
                label.setAlignment(Qt.AlignHCenter)
                self.ui_elements["labels"][(i, j)] = label
                vbox.addWidget(label)

                list_widget = QListWidget()
                self.ui_elements["list_widgets"][i, j] = list_widget
                vbox.addWidget(list_widget)

                self.grid_layout.addLayout(vbox, i, j)

        self.layout.addLayout(self.grid_layout)

        self.setLayout(self.layout)

        self.error_popup = QErrorMessage()

    def show_error(self, message):
        """Displays an error message in a popup dialog.

        Args:
            message (str): The error message to be displayed.
        """
        message = str(message)
        self.error_popup.showMessage(message)


def get_tasks(main_window):
    """Fetches tasks from Todoist and populates the matrix with them.

    Args:
        main_window (MainWindow): The main window object where tasks will be added.
    """
    api = TodoistAPI("0206e65b4253a59d9f888338dea26270cae3cd4c")
    try:
        tasks = api.get_tasks()
        tasks_message = str(tasks[-1].labels[0])
        main_window.show_error(tasks_message)
        for task in tasks:
            main_window.ui_elements["list_widgets"][(0, 0)].addItem(task.content)
    except HTTPError as error:
        main_window.show_error(error)
        print(error)


if __name__ == "__main__":
    # Run the application
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    get_tasks(window)
    sys.exit(app.exec())
