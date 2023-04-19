from dotenv import load_dotenv
import os
import tkinter as tk

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
colors = tk.StringVar(window)
colors.set("green")
graph_color_input = tk.OptionMenu(window, colors, "green", "red", "blue", "yellow", "purple", "black")
graph_color_input.config(bd=2, highlightthickness=0)
graph_color_input.grid(column=1, row=3, sticky="EW")

graph_type_label = tk.Label(text="Type")
graph_type_label.grid(column=2, row=3, sticky="E")
types = tk.StringVar(window)
types.set("int")
graph_type_input = tk.OptionMenu(window, types, "int", "float")
graph_type_input.config(bd=2, highlightthickness=0)
graph_type_input.grid(column=3, row=3, sticky="EW")

create_graph_button = tk.Button(text="Create Graph")
create_graph_button.grid(column=2, row=4, pady=20)





window.mainloop()