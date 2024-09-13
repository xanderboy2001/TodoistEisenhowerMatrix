import sys
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
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.grid_layout = QGridLayout()

        self.labels = {}
        self.list_widgets = {}
        self.button_containers = {}
        self.buttons = {}
        self.line_edits = {}

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
                self.labels[(i, j)] = label
                vbox.addWidget(label)

                list_widget = QListWidget()
                self.list_widgets[i, j] = list_widget
                vbox.addWidget(list_widget)

                self.grid_layout.addLayout(vbox, i, j)

        self.layout.addLayout(self.grid_layout)

        self.setLayout(self.layout)

        self.errorPopup = QErrorMessage()

    def showError(self, message):
        self.errorPopup.showMessage(message)


def getTasks(main_window):
    api = TodoistAPI("0206e65b4253a59d9f888338dea26270cae3cd4c")
    try:
        tasks = api.get_tasks()
        tasks_message = "\n".join([task.content for task in tasks])
        main_window.showError(tasks_message)
    except Exception as error:
        main_window.showError(str(error))
        print(error)
    for task in tasks:
        main_window.list_widgets[(0, 0)].addItem(task.content)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    getTasks(window)
    sys.exit(app.exec())
