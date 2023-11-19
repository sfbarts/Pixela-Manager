import sys
import os
from dotenv import load_dotenv
import random
import requests
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6 import uic
os.environ['PATH'] += r";C:\vips-dev-8.14\bin"
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


def clean_up():
    for file in os.listdir("./image_cache"):
        os.remove(f"./image_cache/{file}")


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
        self.cache_graph_images()
        self.ui.select_graph_menu.currentTextChanged.connect(self.update_graph_image)

    def create_graph(self):
        graph_config = {
            "id": "graph" + str(random.randint(1, 200)),
            "name": self.ui.graph_name_input.text(),
            "unit": self.ui.unit_name_input.text(),
            "type": self.get_unit_type(),
            "color": self.graph_color
        }

        if graph_config["name"] in self.graph_dict.keys():
            # Temporal solution to prevent duplicate names
            print("Name already exists")
            return
        try:
            response = requests.post(url=graph_endpoint, json=graph_config, headers=headers)
        except requests.exceptions.HTTPError:
            self.create_graph()
        else:
            self.graph_dict[graph_config["name"]] = graph_config["id"]
            self.add_graph_to_menu(graph_config["name"])

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
            elif selected_color == self.ui.black_color_picker:
                self.graph_color = "kuro"

    def set_graph_menu(self):
        for graph in list(self.graph_dict.keys()):
            self.ui.select_graph_menu.addItem(graph)

    def add_graph_to_menu(self, graph):
        self.ui.select_graph_menu.addItem(graph)
        self.ui.select_graph_menu.setCurrentText(graph)

    def get_graph_image(self, graph_id):
        try:
            get_graph = requests.get(url=f"{graph_endpoint}/{graph_id}")
        except requests.exceptions.HTTPError:
            print("Could not get image")
            self.get_graph_image(graph_id)
        else:
            with open(f"image_cache/graph.svg", mode="wb") as graph_image:
                graph_image.write(get_graph.content)
                source = pyvips.Source.new_from_file("image_cache/graph.svg")
                png_img = pyvips.Image.new_from_source(source, "", dpi=72)
                target = pyvips.Target.new_to_file(f"image_cache/{graph_id}.png")
                png_img.write_to_target(target, ".png")
                self.update_graph_image()

    def cache_graph_images(self):
        for graph in list(self.graph_dict.values()):
            if not os.path.exists(f"image_cache/{graph}.png"):
                self.get_graph_image(graph)

    def update_graph_image(self):
        graph_key = self.ui.select_graph_menu.currentText()
        graph_id = self.graph_dict[graph_key]
        if os.path.exists(f"image_cache/{graph_id}.png"):
            graph_pixmap = QPixmap(f"image_cache/{graph_id}.png")
            self.ui.graph_image.setPixmap(graph_pixmap)
        else:
            self.get_graph_image(graph_id)
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
    app.aboutToQuit.connect(clean_up)
    main = Main()
    main.show()
    sys.exit(app.exec())
