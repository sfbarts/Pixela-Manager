import sys
import os
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication
from pixela_manager_main import Main
from pixela_manager_credentials import CredentialsDialog
from pixela_manager_splash import SplashScreen


label_text = ""

# clean_up() - Used to remove all cached images when app is closed.
def clean_up():
    for file in os.listdir("./image_cache"):
        os.remove(f"./image_cache/{file}")


# remove_credentials() - Used to delete the .env file that contains the credentials
def remove_credentials():
    os.remove(".env")
    sys.exit()


def save_credentials():
    global label_text
    with open(".env", "a+") as env:
        env.seek(0)
        lines = env.readlines()
        if not lines:
            credentials_dialogue = CredentialsDialog(label_text)
            credentials = credentials_dialogue.get_credentials()
            if credentials != "Error" and credentials is not None:
                username = credentials[0]
                token = credentials[1]
                env.writelines([f'PIXELA_USR="{username}"\n', f'PIXELA_TK="{token}"'])
            elif credentials == "Error":
                label_text = "Invalid credentials"
                return save_credentials()
            else:
                sys.exit()
        env.seek(0)
        load_dotenv(".env")


app = QApplication(sys.argv)
app.aboutToQuit.connect(clean_up)
save_credentials()
USERNAME = os.environ["PIXELA_USR"]
TOKEN = os.environ["PIXELA_TK"]
splash = SplashScreen()
splash.show()
app.processEvents()
main = Main(USERNAME, TOKEN)
main.ui.logout_button.clicked.connect(remove_credentials)
main.show()
splash.finish(main)
sys.exit(app.exec())




