"""
    kampach.gui
    ~~~~~~~~~~~

    Graphical user interface.

    :copyright: 2019 by Kampach Authors, see AUTHORS for more details.
    :license: CeCILL, see LICENSE for more details.
"""

import tkinter as tk
from tkinter import filedialog as fd
from .xmlio import load_xml_file
from .site import Building
from .valuable import QuantitativeValuable
import csv

class KampachUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.load_button = tk.Button(self)
        self.load_button["text"] = "Load XML file"
        self.load_button["command"] = self.load_file
        self.load_button.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def load_file(self):
        file_name = fd.askopenfilename(filetypes=[("XML files", "*.xml")])
        if file_name:
            self.root_valuable = load_xml_file(file_name)
            geom_filename = file_name.replace(".xml", "_geom.csv")
            cost_filename = file_name.replace(".xml", "_cost.csv")
            with open(geom_filename, 'w', newline='') as geom_file:
                with open(cost_filename, 'w', newline='') as cost_file:
                    geom_csv = csv.writer(geom_file)
                    cost_csv = csv.writer(cost_file)
                    geom_csv.writerow(Building.make_geom_csv_header())
                    cost_csv.writerow(QuantitativeValuable.make_cost_csv_header())
                    self.root_valuable.compute_total_cost(geom_csv=geom_csv, cost_csv=cost_csv)

def start():
    root = tk.Tk()
    app = KampachUI(master=root)
    app.mainloop()