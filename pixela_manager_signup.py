from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6 import uic
import requests
import re
from resource_path import *


class SignupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(resource_path("./ui_files/Pixela-Signup-Qt_v001.ui"), self)
        self.ui.ok_button.clicked.connect(self.handle_ok_button)
        self.ui.close_button.clicked.connect(self.handle_close_button)

    def create_user(self):
        result = self.exec()
        if result == QDialog.DialogCode.Accepted:
            username = self.ui.username_input.text()
            token = self.ui.token_input.text()
            terms = "yes" if self.ui.terms_checkbox.isChecked() else False
            not_minor = "yes" if self.ui.minor_checkbox.isChecked() else False
            if not self.validate_user(username, token, terms, not_minor):
                return self.create_user()

            data = {
                "token": token,
                "username": username,
                "agreeTermsOfService": terms,
                "notMinor": not_minor
            }
            pixela_endpoint = "https://pixe.la/v1/users"
            valid_login = False
            while not valid_login:
                try:
                    user_response = requests.post(url=pixela_endpoint, json=data)
                    user_response.raise_for_status()
                except requests.exceptions.HTTPError:
                    print(user_response.status_code)
                    if user_response.status_code == 503:
                        print("No connection available. Retrying.")
                    elif user_response.status_code == 409:
                        QMessageBox.warning(self, "Invalid Username", f"Username already exists. Try another one.")
                        return self.create_user()
                    else:
                        valid_login = True
                        return "Error"
                else:
                    valid_login = True
                    return username, token
        else:
            return None

    def handle_ok_button(self):
        self.done(1)

    def handle_close_button(self):
        self.done(0)

    def validate_user(self, username, token, terms, not_minor):
        if username == "":
            QMessageBox.warning(self, "Invalid Username", f"Username cannot be empty.")
            return False
        elif not re.match(r'^[a-z][a-z0-9-]{1,32}$', username):
            QMessageBox.warning(self, "Invalid Username", f"Username must be lowercase and it can't start with numbers")
            return False
        elif token == "":
            QMessageBox.warning(self, "Invalid Token", f"Token cannot be empty.")
            return False
        elif len(token) < 8:
            QMessageBox.warning(self, "Invalid Token", f"Token must be at least 8 characters long.")
            return False
        elif not terms:
            QMessageBox.warning(self, "Invalid Terms", f"Terms of Service must be accepted.")
            return False
        elif not not_minor:
            QMessageBox.warning(self, "Invalid Terms", f"You must be an adult or have consend from your parents.")
            return False
        else:
            return True

