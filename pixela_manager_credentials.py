from PyQt6.QtWidgets import QDialog
from PyQt6 import uic
import requests


class CredentialsDialog(QDialog):
    def __init__(self, label_text):
        super().__init__()
        self.ui = uic.loadUi("Pixela-Credentials-Qt_v001.ui", self)
        self.ui.invalid_label.setText(label_text)

    def get_credentials(self):
        result = self.exec()
        username = self.ui.username_input.text()
        token = self.ui.token_input.text()
        if result == QDialog.DialogCode.Accepted:
            headers = {
                "X-USER-TOKEN": token,
            }
            pixela_endpoint = "https://pixe.la/v1/users"
            graph_endpoint = f"{pixela_endpoint}/{username}/graphs"
            try:
                graphs_response = requests.get(url=graph_endpoint, headers=headers)
                graphs_response.raise_for_status()
            except requests.exceptions.HTTPError:
                print(graphs_response.status_code)
                if graphs_response.status_code == 503:
                    return self.get_credentials()
                else:
                    return "Error"
            else:
                return username, token
        else:
            return None