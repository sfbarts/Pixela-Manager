import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6 import uic
import uuid

class Main(QWidget):
    def __init__(self):
        super().__init__()

        # import ui from qt designer
        self.ui = uic.loadUi("Pixela-Manager-Qt_v001.ui", self)

        # connect radio buttons
        self.ui.green_color_picker.toggled.connect(self.get_graph_color)
        self.ui.red_color_picker.toggled.connect(self.get_graph_color)
        self.ui.blue_color_picker.toggled.connect(self.get_graph_color)
        self.ui.yellow_color_picker.toggled.connect(self.get_graph_color)
        self.ui.purple_color_picker.toggled.connect(self.get_graph_color)
        self.ui.black_color_picker.toggled.connect(self.get_graph_color)

        # connect create graph button
        self.ui.create_graph_button.clicked.connect(self.create_graph)

    def create_graph(self):
        graph_config = {
            "id": "graph-" + str(uuid.uuid4()),
            "name": self.ui.graph_name_input.text(),
            "unit": self.ui.unit_name_input.text(),
            "type": self.get_unit_type(),
            "color": self.get_graph_color()
        }
        print(graph_config)

    def get_unit_type(self):
        if self.ui.unit_type_menu.currentText() == "Decimal":
            return "float"
        else:
            return "int"

    def get_graph_color(self):
        selected_color = self.sender()
        if selected_color.isChecked():
            if selected_color == self.ui.green_color_picker:
                print("Green Color Selected")
                return "shibafu"
            if selected_color == self.ui.red_color_picker:
                return "momiji"
            if selected_color == self.ui.blue_color_picker:
                return "sora"
            if selected_color == self.ui.yellow_color_picker:
                return "ichou"
            if selected_color == self.ui.purple_color_picker:
                return "ajisai"
            if selected_color == self.ui.kuro_color_picker:
                return "kuro"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec())