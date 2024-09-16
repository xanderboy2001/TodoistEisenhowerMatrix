#!./.venv/bin/python
"""This module implements the Eisenhower Matrix GUI and integrates with Todoist API."""

import sys
import keyring
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
    QMainWindow,
    QPushButton,
    QDialog,
    QLineEdit,
)

KEYRING_SERVICE = "TodoistAPI"
KEYRING_USERNAME = "default_user"


class APIKeyPrompt(QDialog):
    """Dialog to prompt user for Todoist API key."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Todoist API Key")

        self.layout = QVBoxLayout()
        self.label = QLabel("Please enter your Todoist API Key:")
        self.layout.addWidget(self.label)

        self.api_key_input = QLineEdit(self)
        self.layout.addWidget(self.api_key_input)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.save_api_key)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)

    def save_api_key(self):
        """Saves the API key to the keyring"""
        todoist_api_key = self.api_key_input.text()
        if todoist_api_key:
            keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, todoist_api_key)
            self.accept()


class MainWindow(QMainWindow):
    """Main window for the Eisenhower Matrix application."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eisenhower Matrix")
        self.setCentralWidget(CentralWidget())


class CentralWidget(QWidget):
    """Central Widget"""

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
            "Urgent/Not Important",
            "Not Urgent/Important",
            "Not Urgent/Not Important",
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

        button = QPushButton("Refresh")
        todoist_api_key = fetch_or_prompt_api_key()
        button.clicked.connect(lambda: get_tasks(todoist_api_key, self))
        self.layout.addWidget(button)

        self.setLayout(self.layout)

        self.error_popup = QErrorMessage()

    def show_error(self, message):
        """Displays an error message in a popup dialog.

        Args:
            message (str): The error message to be displayed.
        """
        message = str(message)
        self.error_popup.showMessage(message)


def get_stored_api_key():
    """Retrieves the stored API key from keyring"""
    return keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)


def fetch_or_prompt_api_key():
    """Fetches API key from keyring or prompts the user if not available"""
    todoist_api_key = get_stored_api_key()

    if not todoist_api_key:
        dialog = APIKeyPrompt()
        if dialog.exec():
            todoist_api_key = get_stored_api_key()
        else:
            sys.exit()

    return todoist_api_key


def get_tasks(todoist_api_key, central_widget):
    """Fetches tasks from Todoist and populates the matrix with them.

    Args:
        central_widget (CentralWidget): The main window object where tasks will be added.
    """
    # api = TodoistAPI("0206e65b4253a59d9f888338dea26270cae3cd4c")
    api = TodoistAPI(todoist_api_key)
    try:
        tasks = api.get_tasks()

        for (i, j), list_widget in central_widget.ui_elements["list_widgets"].items():
            list_widget.clear()

        for task in tasks:
            task_labels = task.labels

            for label in task_labels:
                if label in central_widget.quads:
                    quad_index = central_widget.quads.index(label)

                    i, j = divmod(quad_index, 2)
                    central_widget.ui_elements["list_widgets"][(i, j)].addItem(
                        task.content
                    )

    except HTTPError as error:
        central_widget.show_error(error)
        print(error)


if __name__ == "__main__":
    # Run the application
    app = QApplication(sys.argv)
    api_key = fetch_or_prompt_api_key()
    keyring.set_password("TodoistAPI", "EisenhowerMatrix", api_key)
    window = MainWindow()
    window.show()
    get_tasks(api_key, window.centralWidget())
    sys.exit(app.exec())
