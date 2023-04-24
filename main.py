from dotenv import load_dotenv
import os
import json
import requests
import random
import tkinter as tk
os.environ['PATH'] += r";C:\vips-dev-8.14\bin"
import pyvips
from tkcalendar import DateEntry
from datetime import date

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
    graph_name_input.delete(0, 'end')
    graph_unit_input.delete(0, 'end')
    refresh_graphs_options()


def delete_graph():
    selected_graph = [graph for graph in graphs_list if graph["name"] == graph_name.get()]
    delete_endpoint = f"{graph_endpoint}/{selected_graph[0]['id']}"
    response = requests.delete(url=delete_endpoint, headers=headers)
    print(response.text)
    refresh_graphs_options()
    update_image("")


def add_pixel():
    graphs_list = get_graphs_list()
    selected_graph = [graph for graph in graphs_list if graph["name"] == graph_name.get()]
    date_selected = date_input.get_date().strftime("%Y%m%d")
    add_pixel_endpoint = f"{graph_endpoint}/{selected_graph[0]['id']}"
    pixel_config = {
        "date": date_selected,
        "quantity": pixel_units_input.get(),
        "optionalData": json.dumps(description_input.get()),
    }

    response = requests.post(url=add_pixel_endpoint, json=pixel_config, headers=headers)
    update_image("")
    pixel_units_input.delete(0, 'end')
    description_input.delete(0, 'end')


def load_image():
    graphs_list = get_graphs_list()
    selected_graph = [graph for graph in graphs_list if graph["name"] == graph_name.get()]
    id = selected_graph[0]['id']
    with open(f"graph.svg", mode="wb") as graph_image:
        get_graph = requests.get(url=f"{graph_endpoint}/{id}")
        img = get_graph.content
        graph_image.write(img)
        source = pyvips.Source.new_from_file("./graph.svg")
        png_img = pyvips.Image.new_from_source(source, "", dpi=72)
        target = pyvips.Target.new_to_file(f"./graph.png")
        png_img.write_to_target(target, ".png")


def update_image(value):
    load_image()
    image.config(file=f"./graph.png")
    label.config(image=image)


def get_graphs_list():
    graphs_response = requests.get(url=graph_endpoint, headers=headers)
    graphs_response.raise_for_status()
    graphs_data = graphs_response.json()
    return graphs_data["graphs"]


def refresh_graphs_options():
    graph_name_options['menu'].delete(0, 'end')
    new_graphs_names = [graph["name"] for graph in get_graphs_list()]
    graph_name.set(new_graphs_names[0])

    for graph in new_graphs_names:
        graph_name_options['menu'].add_command(label=graph, command=tk._setit(graph_name, graph, update_image))



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

edit_graph_section = tk.Label(text="Graph Manager")
edit_graph_section.grid(column=0, row=5)

select_graph_label = tk.Label(text="Select Graph")
select_graph_label.grid(column=0, row=6)

graphs_list = get_graphs_list()
graphs_names = [graph["name"] for graph in graphs_list]
graph_name = tk.StringVar(window)
graph_name.set(graphs_names[0])
graph_name_options = tk.OptionMenu(window, graph_name, *graphs_names, command=update_image)
graph_name_options.config(bd=2, highlightthickness=0)
graph_name_options.grid(column=1, row=6, sticky="EW")

delete_graph_button = tk.Button(text="Delete Graph", command=delete_graph)
delete_graph_button.grid(column=3, row=6, pady=20)

pixel_units_label = tk.Label(text="Units:")
pixel_units_label.grid(column=0, row=7)
pixel_units_input = tk.Entry()
pixel_units_input.grid(column=1, row=7)
date_label = tk.Label(text="Date:")
date_label.grid(column=2, row=7)
date_input = DateEntry(window, selectmode='day')
date_input.grid(column=3, row=7)

description_input = tk.Entry()
description_input.insert(tk.END, "Optional description")
description_input.grid(column=0, row=8, columnspan=4, rowspan=2, sticky="NSEW")


add_pixel_button = tk.Button(text="Add Pixel", command=add_pixel)
add_pixel_button.grid(column=3, row=11)


load_image()
image = tk.PhotoImage(file=f"./graph.png", width=700, height=300)
label = tk.Label(image=image)
label.grid(column=0, row=15, columnspan=4)

window.mainloop()