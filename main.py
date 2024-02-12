import sys
import os
import subprocess
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication
from pixela_manager_main import Main
from pixela_manager_credentials import CredentialsDialog
from pixela_manager_splash import SplashScreen
from resource_path import *


label_text = ""
appdata_path = os.getenv('APPDATA')
app_file_folder = os.path.join(appdata_path, 'Pixela-Manager')
env_file = os.path.join(app_file_folder, ".env")
images_folder = os.path.join(app_file_folder, "image_cache")


# Create an app data folder if it does not exist
def setup_app_data_folder():
    if not os.path.exists(app_file_folder):
        os.makedirs(app_file_folder)


# clean_up() - Used to remove all cached images when app is closed.
def clean_up():
    for file in os.listdir(images_folder):
        os.remove(os.path.join(images_folder, f"{file}"))


# remove_credentials() - Used to delete the .env file that contains the credentials
def remove_credentials():
    os.remove(resource_path(env_file))
    clean_up()
    sys.exit()


def save_credentials():
    global label_text
    with open(resource_path(env_file), "a+") as env:
        env.seek(0)
        lines = env.readlines()
        if not lines:
            credentials_dialogue = CredentialsDialog(label_text)
            credentials = credentials_dialogue.get_credentials()
            if credentials != "Invalid" and credentials is not None:
                username = credentials[0]
                token = credentials[1]
                env.writelines([f'PIXELA_USR="{username}"\n', f'PIXELA_TK="{token}"'])
            elif credentials == "Invalid":
                label_text = "Invalid credentials"
                return save_credentials()
            else:
                sys.exit()
        env.seek(0)
        load_dotenv(resource_path(env_file))


setup_app_data_folder()
app = QApplication(sys.argv)
app.aboutToQuit.connect(clean_up)
save_credentials()
subprocess.run(["attrib", "+H", env_file], check=True)
USERNAME = os.environ["PIXELA_USR"]
TOKEN = os.environ["PIXELA_TK"]
splash = SplashScreen()
splash.show()
app.processEvents()
main = Main(USERNAME, TOKEN, app_file_folder)
main.ui.logout_button.clicked.connect(remove_credentials)
main.show()
splash.finish(main)
sys.exit(app.exec())




