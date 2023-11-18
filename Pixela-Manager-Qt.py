import sys
import os
os.environ['PATH'] += r";C:\vips-dev-8.14\bin"
from dotenv import load_dotenv
import random
import requests
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QSize
from PyQt6 import uic
import pyvips


load_dotenv("./.env")
USERNAME = os.environ["PIXELA_USR"]
TOKEN = os.environ["PIXELA_TK"]

headers = {
    "X-USER-TOKEN": TOKEN,
}

pixela_endpoint = "https://pixe.la/v1/users"
graph_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs"


def get_graphs_list():
    graphs_response = requests.get(url=graph_endpoint, headers=headers)
    graphs_response.raise_for_status()
    graphs_data = graphs_response.json()
    response_dict = {}
    for graph in graphs_data["graphs"]:
        response_dict[graph["name"]] = graph["id"]
    return response_dict


class Main(QWidget):
    def __init__(self):
        super().__init__()

        # import ui from qt designer
        self.ui = uic.loadUi("Pixela-Manager-Qt_v001.ui", self)

        self.graph_color = ""
        self.graph_dict = get_graphs_list()

        # connect radio buttons
        self.ui.green_color_picker.toggled.connect(self.get_graph_color)
        self.ui.red_color_picker.toggled.connect(self.get_graph_color)
        self.ui.blue_color_picker.toggled.connect(self.get_graph_color)
        self.ui.yellow_color_picker.toggled.connect(self.get_graph_color)
        self.ui.purple_color_picker.toggled.connect(self.get_graph_color)
        self.ui.black_color_picker.toggled.connect(self.get_graph_color)

        # connect create graph button
        self.ui.create_graph_button.clicked.connect(self.create_graph)

        # connect delete graph button
        self.ui.delete_graph_button.clicked.connect(self.delete_graph)

        self.set_graph_menu()
        self.get_graph_image()
        self.ui.select_graph_menu.currentTextChanged.connect(self.update_graph_image)

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

    def set_graph_menu(self):
        for graph in list(self.graph_dict.keys()):
            self.ui.select_graph_menu.addItem(graph)

    def get_graph_image(self):
        graph_key = self.ui.select_graph_menu.currentText()
        graph_id = self.graph_dict[graph_key]
        try:
            get_graph = requests.get(url=f"{graph_endpoint}/{graph_id}")
        except requests.exceptions.HTTPError:
            print("Could not get image")
        else:
            with open(f"graph.svg", mode="wb") as graph_image:
                graph_image.write(get_graph.content)
                source = pyvips.Source.new_from_file("./graph.svg")
                png_img = pyvips.Image.new_from_source(source, "", dpi=72)
                target = pyvips.Target.new_to_file(f"./{graph_id}.png")
                png_img.write_to_target(target, ".png")
                graph_pixmap = QPixmap(f"./{graph_id}.png")
                self.ui.graph_image.setPixmap(graph_pixmap)

    def update_graph_image(self):
        graph_key = self.ui.select_graph_menu.currentText()
        graph_id = self.graph_dict[graph_key]
        if os.path.exists(f"./{graph_id}.png"):
            graph_pixmap = QPixmap(f"./{graph_id}.png")
            self.ui.graph_image.setPixmap(graph_pixmap)
        else:
            self.get_graph_image()
            self.update_graph_image()

    def delete_graph(self):
        graph_key = self.ui.select_graph_menu.currentText()
        graph_id = self.graph_dict[graph_key]
        delete_endpoint = f"{graph_endpoint}/{graph_id}"

        try:
            response = requests.delete(url=delete_endpoint, headers=headers)
        except requests.exceptions.HTTPError:
            print("Could not delete graph, try again")
        else:
            self.graph_dict.pop(graph_key)
            self.ui.select_graph_menu.removeItem(self.ui.select_graph_menu.currentIndex())
            print(graph_id)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec())