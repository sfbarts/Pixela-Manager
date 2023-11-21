import sys
import os
from dotenv import load_dotenv
import random
import requests
import json
import re
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QDate, QThread, pyqtSignal
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


# get_graphs_list() - get list of graphs from pixela and store relevant details
def get_graphs_list():
    try:
        graphs_response = requests.get(url=graph_endpoint, headers=headers)
        graphs_response.raise_for_status()
    except requests.exceptions.HTTPError:
        return get_graphs_list()
    else:
        graphs_data = graphs_response.json()
        response_dict = {}
        for graph in graphs_data["graphs"]:
            response_dict.setdefault(graph["name"], {})
            response_dict[graph["name"]]["id"] = graph["id"]
            response_dict[graph["name"]]["unit"] = graph["unit"]
        return response_dict


# clean_up() - Used to remove all cached images when app is closed.
def clean_up():
    for file in os.listdir("./image_cache"):
        os.remove(f"./image_cache/{file}")


# WorkerThread is a class that is used to perform a task in parallel.
# In this case, it shows a progress bar while executing.
class WorkerThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, method):
        super().__init__()
        self.method = method

    def run(self):
        self.method()
        self.finished_signal.emit()


# validate_units() - Used to verify that input is a number
def validate_units(value):
    pattern = re.compile(r'^[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?$')
    return bool(pattern.match(value))


class Main(QWidget):
    def __init__(self):
        super().__init__()

        # import ui from qt designer
        self.ui = uic.loadUi("Pixela-Manager-Qt_v001.ui", self)
        self.ui.progress_bar.hide()

        # initialize variables that will be used on other methods
        self.graph_color = ""
        self.graph_dict = get_graphs_list()

        # connect radio buttons toggled signals for color picking to get_graph_color()
        self.ui.green_color_picker.toggled.connect(self.get_graph_color)
        self.ui.red_color_picker.toggled.connect(self.get_graph_color)
        self.ui.blue_color_picker.toggled.connect(self.get_graph_color)
        self.ui.yellow_color_picker.toggled.connect(self.get_graph_color)
        self.ui.purple_color_picker.toggled.connect(self.get_graph_color)
        self.ui.black_color_picker.toggled.connect(self.get_graph_color)

        # connect create graph button clicked signal to create_graph()
        self.ui.create_graph_button.clicked.connect(self.create_graph)

        # connect delete graph button clicked signal to delete_graph()
        self.ui.delete_graph_button.clicked.connect(self.delete_graph)

        # call methods to set up initial graph manager section
        self.set_graph_menu()
        self.current_graph_key = self.ui.select_graph_menu.currentText()
        self.current_graph_id = self.graph_dict[self.current_graph_key]["id"]
        self.cache_graph_images()
        self.update_graph_image()

        # connect graph selector menu currentTextChanged signal to update_graph()
        self.ui.select_graph_menu.currentTextChanged.connect(self.update_graph)

        # set date picker to current date on load and connect it to start task slot
        self.ui.date_picker.setDate(QDate.currentDate())
        self.ui.date_picker.dateChanged.connect(self.start_task)

        # connect update pixel button clicked signal to add_pixel()
        self.ui.update_pixel_button.clicked.connect(self.add_pixel)

        # initialize pixel details section
        self.set_pixel_details()

    # CREATE GRAPH SECTION ------------------------------------
    # create_graph() - uses input to create a new graph in Pixela. Graph and Pixel Manager sections update accordingly.
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
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return self.create_graph()
        else:
            self.graph_dict.setdefault(graph_config["name"], {})
            self.graph_dict[graph_config["name"]]["id"] = graph_config["id"]
            self.graph_dict[graph_config["name"]]["unit"] = graph_config["unit"]
            self.add_graph_to_menu(graph_config["name"])
            self.update_graph()
            self.ui.graph_name_input.clear()
            self.ui.unit_name_input.clear()

    # get_unit_type() - Auxiliary method to format unit name input to the correct value accepted by Pixela.
    def get_unit_type(self):
        if self.ui.unit_type_menu.currentText() == "Decimal":
            return "float"
        else:
            return "int"

    # get_graph_color() -Slot used to update the selected color. It sets the color to the equivalent Pixela value.
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

    # add_graph_to_menu() - Auxiliary method to add new items to the graph selection menu on graph creation.
    def add_graph_to_menu(self, graph):
        self.ui.select_graph_menu.addItem(graph)
        self.ui.select_graph_menu.setCurrentText(graph)

    # GRAPH MANAGER SECTION --------------------------------------------------
    # set_graph_menu() - Auxiliary method to update the graph selection menu on start.
    def set_graph_menu(self):
        for graph in list(self.graph_dict.keys()):
            self.ui.select_graph_menu.addItem(graph)

    # get_graph_image() - Auxiliary method to get a graph image from pixela and convert it to PNG.
    def get_graph_image(self, graph_id):
        try:
            get_graph = requests.get(url=f"{graph_endpoint}/{graph_id}")
        except requests.exceptions.HTTPError:
            print("Could not get image")
            return self.get_graph_image(graph_id)
        else:
            with open(f"image_cache/graph.svg", mode="wb") as graph_image:
                graph_image.write(get_graph.content)
                source = pyvips.Source.new_from_file("image_cache/graph.svg")
                png_img = pyvips.Image.new_from_source(source, "", dpi=72)
                target = pyvips.Target.new_to_file(f"image_cache/{graph_id}.png")
                png_img.write_to_target(target, ".png")

    # cache_graph_images() - Auxiliary method to save the latest graph image for each graph on start
    def cache_graph_images(self):
        graphs = [graph["id"] for graph in self.graph_dict.values()]
        for graph in graphs:
            if not os.path.exists(f"image_cache/{graph}.png"):
                self.get_graph_image(graph)

    # update_graph_image() - Auxiliary method to change the current graph images based on selected graph
    def update_graph_image(self):
        if os.path.exists(f"image_cache/{self.current_graph_id}.png"):
            graph_pixmap = QPixmap(f"image_cache/{self.current_graph_id}.png")
            self.ui.graph_image.setPixmap(graph_pixmap)
        else:
            self.get_graph_image(self.current_graph_id)
            self.update_graph_image()

    # update_graph() - Method to run update_graph_image() and start_task() at once
    def update_graph(self):
        self.current_graph_key = self.ui.select_graph_menu.currentText()
        self.current_graph_id = self.graph_dict[self.current_graph_key]["id"]
        self.start_task()
        self.update_graph_image()

    # delete_graph() - deletes graph from Pixela based on selected graph.
    def delete_graph(self):
        delete_endpoint = f"{graph_endpoint}/{self.current_graph_id}"

        try:
            response = requests.delete(url=delete_endpoint, headers=headers)
        except requests.exceptions.HTTPError:
            print("Could not delete graph, try again")
            return self.delete_graph()
        else:
            self.graph_dict.pop(self.current_graph_key)
            self.ui.select_graph_menu.removeItem(self.ui.select_graph_menu.currentIndex())

    # MANAGE PIXEL SECTION -------------------------------------------------------------
    # get_pixel_details() - Auxiliary method to get data from a specific pixel on Pixela.
    def get_pixel_details(self):
        graph_unit = self.graph_dict[self.current_graph_key]["unit"]
        date_selected = self.ui.date_picker.date().toString("yyyyMMdd")
        date_formatted = self.ui.date_picker.date().toString("yyyy/MM/dd")
        self.ui.pixel_units_label.setText(f"{graph_unit.capitalize()}:")
        get_pixel_endpoint = f"{graph_endpoint}/{self.current_graph_id}/{date_selected}"

        try:
            response = requests.get(url=get_pixel_endpoint, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.status_code == 404:
                return response.json()

            print("Could not get details")
            return self.get_pixel_details()
        else:
            pixel_data = response.json()
            pixel_data["unit"] = graph_unit
            pixel_data["date"] = date_formatted
            if pixel_data["optionalData"] == '""':
                pixel_data["optionalData"] = "No description added."
            return pixel_data

    # set_pixel_details() - updates the pixel details section based on data returned by get_pixel_details()
    def set_pixel_details(self):
        pixel_details = self.get_pixel_details()
        if "message" in pixel_details.keys():
            self.ui.pixel_details_label.setText("No Pixel added on this date yet.")
            self.ui.update_pixel_button.setText("Add Pixel")
            return

        self.ui.pixel_details_label.setText(f"Date: {pixel_details['date']}\n"
                                            f"Info: {pixel_details['quantity']} {pixel_details['unit']}\n"
                                            f"Description: {pixel_details['optionalData']}")
        self.ui.update_pixel_button.setText("Update Pixel")

    # add_pixel() - uses input to create a pixel for a specific date based on selected graph.
    def add_pixel(self):
        date_selected = self.ui.date_picker.date().toString("yyyyMMdd")
        add_pixel_endpoint = f"{graph_endpoint}/{self.current_graph_id}/{date_selected}"
        quantity = self.ui.pixel_units_input.text()
        quantity_is_number = validate_units(quantity)
        if not quantity_is_number:
            return print("Quantity must be a number")

        description = json.dumps(self.ui.pixel_description_box.toPlainText())

        pixel_config = {
            "quantity": quantity,
            "optionalData": description,
        }

        try:
            response = requests.put(url=add_pixel_endpoint, json=pixel_config, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return self.add_pixel()
        else:
            print("Pixel Added")
            self.get_graph_image(self.current_graph_id)
            self.update_graph()
            self.ui.pixel_units_input.clear()
            self.ui.pixel_description_box.clear()

    # start_task() - launches the worker thread to run set_pixel_details in parallel. Allows progress bar to be shown.
    def start_task(self):
        self.ui.progress_bar.setValue(random.randint(25, 75))
        self.ui.progress_bar.show()

        self.worker_thread = WorkerThread(self.set_pixel_details)
        self.worker_thread.finished_signal.connect(self.task_complete)
        self.worker_thread.start()

    # task_complete() - hide progress bar after pixel details are loaded
    def task_complete(self):
        self.ui.progress_bar.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(clean_up)
    main = Main()
    main.show()
    sys.exit(app.exec())
