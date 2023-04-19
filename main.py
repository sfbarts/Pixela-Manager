from dotenv import load_dotenv
import os
import requests
import random
import tkinter as tk

load_dotenv("./.env")
USERNAME = os.environ["PIXELA_USR"]
TOKEN = os.environ["PIXELA_TK"]

headers = {
    "X-USER-TOKEN": TOKEN,
}
print(USERNAME)
pixela_endpoint = "https://pixe.la/v1/users"
graph_endpoint = f"{pixela_endpoint}/{USERNAME}/graphs"

colors = {
    "black": "kuro",
    "green": "shibafu",
    "red": "momiji",
    "blue": "sora",
    "yellow": "ichou",
    "purple": "ajisai",
    "black": "kuro"
}


def create_graph():
    graph_config = {
        "id": "graph" + str(random.randint(1, 200)),
        "name": graph_name_input.get(),
        "unit": graph_unit_input.get(),
        "type": unit_type.get(),
        "color": colors[color.get()]
    }
    print(graph_config)
    response = requests.post(url=graph_endpoint, json=graph_config, headers=headers)
    print(response.text)


def delete_graph():
    selected_graph = [graph for graph in graphs_list if graph["name"] == graph_name.get()]
    delete_endpoint = f"{graph_endpoint}/{selected_graph[0]['id']}"
    response = requests.delete(url=delete_endpoint, headers=headers)
    print(response.text)


window = tk.Tk()
window.title("Pixela Manager")
window.config(padx=30, pady=60)

title_label = tk.Label(text="Pixela Manager", font=("Arial", 20, "bold"))
title_label.place(x=115, y=-40)

create_section_label = tk.Label(text="Create Graph")
create_section_label.grid(column=0, row=1)

graph_name_label = tk.Label(text="Name")
graph_name_label.grid(column=0, row=2)
graph_name_input = tk.Entry()
graph_name_input.grid(column=1, row=2, sticky="EW")

graph_unit_label = tk.Label(text="Unit")
graph_unit_label.grid(column=2, row=2, sticky="E")
graph_unit_input = tk.Entry()
graph_unit_input.grid(column=3, row=2, sticky="EW")

graph_color_label = tk.Label(text="Color")
graph_color_label.grid(column=0, row=3)
color = tk.StringVar(window)
color.set("green")
graph_color_input = tk.OptionMenu(window, color, "green", "red", "blue", "yellow", "purple", "black")
graph_color_input.config(bd=2, highlightthickness=0)
graph_color_input.grid(column=1, row=3, sticky="EW")

graph_type_label = tk.Label(text="Type")
graph_type_label.grid(column=2, row=3, sticky="E")
unit_type = tk.StringVar(window)
unit_type.set("int")
graph_type_input = tk.OptionMenu(window, unit_type, "int", "float")
graph_type_input.config(bd=2, highlightthickness=0)
graph_type_input.grid(column=3, row=3, sticky="EW")

create_graph_button = tk.Button(text="Create", command=create_graph)
create_graph_button.grid(column=2, row=4, pady=20)

delete_graph_label = tk.Label(text="Delete Graph")
delete_graph_label.grid(column=0, row=5)
graphs_response = requests.get(url=graph_endpoint, headers=headers)
graphs_response.raise_for_status()
graphs_data = graphs_response.json()
graphs_list = graphs_data["graphs"]
graphs_names = [graph["name"] for graph in graphs_list]
graph_name = tk.StringVar(window)
graph_name.set(graphs_names[0])
graph_name_options = tk.OptionMenu(window, graph_name, *graphs_names)
graph_name_options.config(bd=2, highlightthickness=0)
graph_name_options.grid(column=1, row=5, sticky="EW")

delete_graph_button = tk.Button(text="Delete", command=delete_graph)
delete_graph_button.grid(column=2, row=5, pady=20)






window.mainloop()