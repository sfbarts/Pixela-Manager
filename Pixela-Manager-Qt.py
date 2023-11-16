import sys
import os
from dotenv import load_dotenv
import random
import requests
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6 import uic

load_dotenv("./.env")
USERNAME = os.environ["PIXELA_USR"]
TOKEN = os.environ["PIXELA_TK"]

headers = {
    "X-USER-TOKEN": TOKEN,
}

pixela_endpoint = "https://pixe.la/v1/users"
graph_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs"

class Main(QWidget):
    def __init__(self):
        super().__init__()

        # import ui from qt designer
        self.ui = uic.loadUi("Pixela-Manager-Qt_v001.ui", self)

        self.graph_color = ""

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
            "id": "graph" + str(random.randint(1, 200)),
            "name": self.ui.graph_name_input.text(),
            "unit": self.ui.unit_name_input.text(),
            "type": self.get_unit_type(),
            "color": self.graph_color
        }
        print(graph_config)
        try:
            response = requests.post(url=graph_endpoint, json=graph_config, headers=headers)
            print(response.text)
        except requests.exceptions.HTTPError:
            print(response.text)
            print("Could not add the new graph, try again")

    def get_unit_type(self):
        if self.ui.unit_type_menu.currentText() == "Decimal":
            return "float"
        else:
            return "int"

    def get_graph_color(self):
        selected_color = self.sender()
        if selected_color.isChecked():
            if selected_color == self.ui.green_color_picker:
                self.graph_color = "shibafu"
            elif selected_color == self.ui.red_color_picker:
                self.graph_color = "momiji"
            elif selected_color == self.ui.blue_color_picker:
                self.graph_color = "sora"
            elif selected_color == self.ui.yellow_color_picker:
                self.graph_color = "ichou"
            elif selected_color == self.ui.purple_color_picker:
                self.graph_color = "ajisai"
            elif selected_color == self.ui.kuro_color_picker:
                self.graph_color = "kuro"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec())