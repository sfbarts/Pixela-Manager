from PyQt6.QtWidgets import QDialog
from PyQt6 import uic
from pixela_manager_signup import SignupDialog
import requests
from resource_path import *

class CredentialsDialog(QDialog):
    def __init__(self, label_text):
        super().__init__()
        self.ui = uic.loadUi(resource_path(resource_path("./ui_files/Pixela-Credentials-Qt_v001.ui")), self)
        self.ui.invalid_label.setText(label_text)
        self.ui.signup_button.clicked.connect(self.show_signup_dialogue)
        self.ui.ok_button.clicked.connect(self.handle_ok_button)
        self.ui.close_button.clicked.connect(self.handle_close_button)

    def get_credentials(self):
        result = self.exec()

        if result == 1:
            username = self.ui.username_input.text()
            token = self.ui.token_input.text()
            headers = {
                "X-USER-TOKEN": token,
            }
            pixela_endpoint = "https://pixe.la/v1/users"
            graph_endpoint = f"{pixela_endpoint}/{username}/graphs"
            valid_login = False
            while not valid_login:
                try:
                    graphs_response = requests.get(url=graph_endpoint, headers=headers)
                    print(graphs_response.json())
                    graphs_response.raise_for_status()
                except requests.exceptions.HTTPError:
                    if graphs_response.status_code == 503:
                        print("No connection available. Retrying.")
                    else:
                        valid_login = True
                        return "Invalid"
                else:
                    valid_login = True
                    return username, token
        elif result == 0:
            return None
        elif result == 5:
            signup_dialogue = SignupDialog()
            signup_credentials = signup_dialogue.create_user()
            return signup_credentials

    def handle_ok_button(self):
        self.done(1)

    def handle_close_button(self):
        self.done(0)

    def show_signup_dialogue(self):
        self.done(5)
