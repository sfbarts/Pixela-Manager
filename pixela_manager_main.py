import os
import random
import requests
import json
import re
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QDate, QThread, pyqtSignal
from PyQt6 import uic
from resource_path import *

os.environ['PATH'] += r";C:\vips-dev-8.14\bin"
import pyvips


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
    def __init__(self, username, token):
        super().__init__()
        self.headers = {
            "X-USER-TOKEN": token,
        }
        pixela_endpoint = "https://pixe.la/v1/users"
        self.graph_endpoint = f"{pixela_endpoint}/{username}/graphs"

        # import ui from qt designer
        self.ui = uic.loadUi(resource_path("./ui_files/Pixela-Manager-Qt_v001.ui"), self)
        self.ui.progress_bar.hide()

        # initialize variables that will be used on other methods
        self.graph_color = ""
        self.graph_unit = ""
        self.pixel_data = {}
        self.current_graph_key = ""
        self.current_graph_id = ""
        self.graph_dict = self.get_graphs_list()

        # connect radio buttons toggled signals for color picking to get_graph_color()
        self.ui.green_color_picker.toggled.connect(self.get_graph_color)
        self.ui.red_color_picker.toggled.connect(self.get_graph_color)
        self.ui.blue_color_picker.toggled.connect(self.get_graph_color)
        self.ui.yellow_color_picker.toggled.connect(self.get_graph_color)
        self.ui.purple_color_picker.toggled.connect(self.get_graph_color)
        self.ui.black_color_picker.toggled.connect(self.get_graph_color)

        # connect create graph button clicked signal to create_graph()
        self.ui.create_graph_button.clicked.connect(self.validate_graph_creation)

        # connect delete graph button clicked signal to delete_graph()
        self.ui.delete_graph_button.clicked.connect(self.delete_graph)

        # call methods to set up initial graph manager section
        self.set_graph_menu()
        self.setup_graph_details()
        self.cache_graph_images()
        self.update_graph_image()

        # connect graph selector menu currentTextChanged signal to handle_graph_change()
        self.ui.select_graph_menu.currentTextChanged.connect(self.handle_graph_change)

        # set date picker to current date on load and connect it to start task slot
        self.ui.date_picker.setDate(QDate.currentDate())
        self.ui.date_picker.dateChanged.connect(lambda: self.start_task(self.get_pixel_details,
                                                                        self.handle_date_change_finish))

        # connect delete pixel button clicked signal to start task
        self.ui.delete_pixel_button.clicked.connect(lambda: self.start_task(self.delete_pixel,
                                                                            self.handle_update_pixel_finish))

        # connect update pixel button clicked signal to validate_pixel_creation()
        self.ui.update_pixel_button.clicked.connect(self.validate_pixel_creation)

        # initialize pixel details section
        self.get_pixel_details()
        self.set_pixel_details()

    # INITIAL GRAPH LIST SETUP ---------------------------------
    # get_graphs_list() - get list of graphs from pixela and store relevant details
    def get_graphs_list(self):
        try:
            graphs_response = requests.get(url=self.graph_endpoint, headers=self.headers)
            graphs_response.raise_for_status()
        except requests.exceptions.HTTPError:
            return self.get_graphs_list()
        else:
            graphs_data = graphs_response.json()
            response_dict = {}
            for graph in graphs_data["graphs"]:
                response_dict.setdefault(graph["name"], {})
                response_dict[graph["name"]]["id"] = graph["id"]
                response_dict[graph["name"]]["unit"] = graph["unit"]
            return response_dict

    def setup_graph_details(self):
        if self.graph_dict:
            self.current_graph_key = self.ui.select_graph_menu.currentText()
            self.current_graph_id = self.graph_dict[self.current_graph_key]["id"]

    # CREATE GRAPH SECTION ------------------------------------
    # validate_graph_creation() - Makes sure names are unique and makes sure all inputs are present.
    def validate_graph_creation(self):
        name = self.ui.graph_name_input.text()
        unit = self.ui.unit_name_input.text()
        color = self.graph_color
        unit_type = self.get_unit_type()

        if name in self.graph_dict.keys():
            QMessageBox.warning(self, "Invalid Graph", f"{name} already exists.")
            return
        if name == "" or unit == "" or color == "":
            QMessageBox.warning(self, "Invalid Graph", "Please specify name, unit and color.")
            return
        else:
            self.start_task(lambda: self.create_graph(name, unit, color, unit_type),
                            self.handle_create_graph_finish)

    # create_graph() - uses input to create a new graph in Pixela. Graph and Pixel Manager sections update accordingly.
    def create_graph(self, name, unit, color, unit_type):
        graph_config = {
            "id": "graph" + str(random.randint(1, 200)),
            "name": name,
            "unit": unit,
            "type": unit_type,
            "color": color
        }

        try:
            response = requests.post(url=self.graph_endpoint, json=graph_config, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return self.create_graph(name, unit, color, unit_type)
        else:
            self.graph_dict.setdefault(graph_config["name"], {})
            self.graph_dict[graph_config["name"]]["id"] = graph_config["id"]
            self.graph_dict[graph_config["name"]]["unit"] = graph_config["unit"]
            self.get_graph_image(graph_config["id"])
            self.current_graph_key = graph_config["name"]
            self.current_graph_id = graph_config["id"]
            self.get_pixel_details()

    # handle_create_finish() - Updates ui after graph creation thread is finished.
    def handle_create_graph_finish(self):
        self.add_graph_to_menu(self.current_graph_key)
        self.update_graph()
        self.ui.graph_name_input.clear()
        self.ui.unit_name_input.clear()
        self.ui.progress_bar.hide()

    # add_graph_to_menu() - Auxiliary method to add new items to the graph selection menu on graph creation.
    def add_graph_to_menu(self, graph):
        self.ui.select_graph_menu.addItem(graph)
        self.ui.select_graph_menu.setCurrentText(graph)

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

    # GRAPH MANAGER SECTION --------------------------------------------------
    # set_graph_menu() - Auxiliary method to update the graph selection menu on start.
    def set_graph_menu(self):
        for graph in list(self.graph_dict.keys()):
            self.ui.select_graph_menu.addItem(graph)

    # get_graph_image() - Auxiliary method to get a graph image from pixela and convert it to PNG.
    def get_graph_image(self, graph_id):
        try:
            get_graph = requests.get(url=f"{self.graph_endpoint}/{graph_id}")
        except requests.exceptions.HTTPError:
            print("Could not get image")
            return self.get_graph_image(graph_id)
        else:
            if not os.path.exists(resource_path("image_cache")):
                os.makedirs("image_cache")
            with open(resource_path(f"image_cache/graph.svg"), mode="wb") as graph_image:
                graph_image.write(get_graph.content)
                source = pyvips.Source.new_from_file(resource_path("image_cache/graph.svg"))
                png_img = pyvips.Image.new_from_source(source, "", dpi=72)
                target = pyvips.Target.new_to_file(resource_path(f"image_cache/{graph_id}.png"))
                png_img.write_to_target(target, ".png")

    # cache_graph_images() - Auxiliary method to save the latest graph image for each graph on start
    def cache_graph_images(self):
        if self.graph_dict:
            graphs = [graph["id"] for graph in self.graph_dict.values()]
            for graph in graphs:
                if not os.path.exists(resource_path(f"image_cache/{graph}.png")):
                    self.get_graph_image(graph)
        else:
            self.ui.graph_image.setText("No graphs created yet.")

    # update_graph_image() - Auxiliary method to change the current graph images based on selected graph
    def update_graph_image(self):
        if not self.graph_dict:
            return
        if os.path.exists(resource_path(f"image_cache/{self.current_graph_id}.png")):
            graph_pixmap = QPixmap(resource_path(f"image_cache/{self.current_graph_id}.png"))
            self.ui.graph_image.setPixmap(graph_pixmap)
        else:
            self.get_graph_image(self.current_graph_id)
            self.update_graph_image()

    # delete_graph() - deletes graph from Pixela based on selected graph.
    def delete_graph(self):
        if not self.graph_dict:
            QMessageBox.warning(self, f"Nonexistent Graph ", f"You need to create a graph first.")
            return
        delete_endpoint = f"{self.graph_endpoint}/{self.current_graph_id}"
        try:
            response = requests.delete(url=delete_endpoint, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print("Could not delete graph, try again")
            return self.delete_graph()
        else:
            self.graph_dict.pop(self.current_graph_key)
            self.ui.select_graph_menu.removeItem(self.ui.select_graph_menu.currentIndex())

    # handle_graph_change() - Auxiliary method to update graph manager.
    def handle_graph_change(self):
        if self.graph_dict:
            self.current_graph_key = self.ui.select_graph_menu.currentText()
            self.current_graph_id = self.graph_dict[self.current_graph_key]["id"]
            self.start_task(self.get_pixel_details, self.handle_graph_change_finish)
        else:
            self.ui.graph_image.clear()
            self.ui.graph_image.setText("No graphs created yet.")

    # update_graph() - Method to run update_graph_image() and set_pixel_details() at once
    def update_graph(self):
        self.update_graph_image()
        self.set_pixel_details()

    # handle_graph_change_finish() - Auxiliary method run after manager is updated to refresh ui.
    def handle_graph_change_finish(self):
        self.update_graph()
        self.ui.progress_bar.hide()

    # MANAGE PIXEL SECTION -------------------------------------------------------------
    # get_pixel_details() - Auxiliary method to get data from a specific pixel on Pixela.
    def get_pixel_details(self):
        if not self.graph_dict:
            return

        self.graph_unit = self.graph_dict[self.current_graph_key]["unit"].capitalize()
        date_selected = self.ui.date_picker.date().toString("yyyyMMdd")
        date_formatted = self.ui.date_picker.date().toString("yyyy/MM/dd")
        get_pixel_endpoint = f"{self.graph_endpoint}/{self.current_graph_id}/{date_selected}"

        try:
            response = requests.get(url=get_pixel_endpoint, headers=self.headers)
            print("response on get details:", response.json())
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.status_code == 404:
                self.pixel_data = response.json()
                return response.json()

            print("Could not get details")
            return self.get_pixel_details()
        else:
            pixel_data = response.json()
            pixel_data["unit"] = self.graph_unit
            pixel_data["date"] = date_formatted
            if "optionalData" not in pixel_data:
                pixel_data["optionalData"] = "No description added."
            elif pixel_data["optionalData"] == '""':
                pixel_data["optionalData"] = "No description added."
            self.pixel_data = pixel_data

    # set_pixel_details() - updates the pixel details section based on data returned by get_pixel_details()
    def set_pixel_details(self):
        pixel_details = self.pixel_data
        if self.graph_unit:
            self.ui.pixel_units_label.setText(f"{self.graph_unit}:")

        if not pixel_details or "message" in pixel_details.keys():
            self.ui.delete_pixel_button.hide()
            self.ui.pixel_details_label.setText("No Pixel added on this date yet.")
            self.ui.update_pixel_button.setText("Add Pixel")
            return

        self.ui.delete_pixel_button.show()
        self.ui.pixel_details_label.setText(f"Date: {pixel_details['date']}\n"
                                            f"Info: {pixel_details['quantity']} {pixel_details['unit']}\n"
                                            f"Description: {pixel_details['optionalData']}")
        self.ui.update_pixel_button.setText("Update Pixel")

    # handle_date_change_finish() - Update ui after date change update worker is done.
    def handle_date_change_finish(self):
        self.set_pixel_details()
        self.ui.progress_bar.hide()

    # validate_pixel_creation() - Checks that units are present and are valid. Starts add_pixel task if valid.
    def validate_pixel_creation(self):
        if not self.graph_dict:
            QMessageBox.warning(self, f"Nonexistent Graph ", f"You need to create a graph first.")
            return
        unit_name = self.graph_unit
        date_selected = self.ui.date_picker.date().toString("yyyyMMdd")
        quantity = self.ui.pixel_units_input.text()
        quantity_is_number = validate_units(quantity)
        description = self.ui.pixel_description_box.toPlainText()
        if quantity == "":
            QMessageBox.warning(self, f"Missing {unit_name}", f"Please specify {unit_name}.")
        elif not quantity_is_number:
            QMessageBox.warning(self, f"Invalid {unit_name}", f"{unit_name} must be a number.")
        else:
            pixel_config = {
                "quantity": quantity,
            }
            if description != "":
                pixel_config["optionalData"] = json.dumps(description)
            self.start_task(lambda: self.add_pixel(date_selected, pixel_config),
                            self.handle_update_pixel_finish)

    # add_pixel() - uses input to create a pixel for a specific date based on selected graph.
    def add_pixel(self, date_selected, pixel_config):
        add_pixel_endpoint = f"{self.graph_endpoint}/{self.current_graph_id}/{date_selected}"
        try:
            response = requests.put(url=add_pixel_endpoint, json=pixel_config, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return self.add_pixel(date_selected, pixel_config)
        else:
            self.get_graph_image(self.current_graph_id)
            self.get_pixel_details()

    # delete_pixel() - handles pixel deletion.
    def delete_pixel(self):
        date_selected = self.ui.date_picker.date().toString("yyyyMMdd")
        delete_pixel_endpoint = f"{self.graph_endpoint}/{self.current_graph_id}/{date_selected}"
        try:
            response = requests.delete(url=delete_pixel_endpoint, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return self.delete_pixel()
        else:
            self.get_graph_image(self.current_graph_id)
            self.get_pixel_details()

    # handle_update_pixel_finish() - handles ui update after pixel deletion, addition or update.
    def handle_update_pixel_finish(self):
        self.update_graph()
        self.ui.pixel_units_input.clear()
        self.ui.pixel_description_box.clear()
        self.ui.progress_bar.hide()

    # start_task() - launches the worker thread to run set_pixel_details in parallel. Allows progress bar to be shown.
    def start_task(self, start_method, finish_method):
        self.ui.progress_bar.setValue(random.randint(25, 95))
        self.ui.progress_bar.show()

        self.worker_thread = WorkerThread(start_method)
        self.worker_thread.finished_signal.connect(finish_method)
        self.worker_thread.start()
