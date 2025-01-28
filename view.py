import tkinter as tk
from tkinter import ttk, filedialog
import random
import json

from numpy import empty

class GUI:
    def __init__(self, root, generate_instances, greedy_algorithm, local_search):
        self.root = root
        self.generate_instances = generate_instances
        self.greedy_algorithm = greedy_algorithm
        self.local_search = local_search
        self.rectangles = []
        self.L = 0
        self.setup_ui()
    
    def setup_ui(self):
        self.root.title("Optimierungsalgorithmen GUI")

        # Create input fields and place them in UI
        frame_inputs = tk.Frame(self.root)
        frame_inputs.pack(pady=10)

        tk.Label(frame_inputs, text="Anzahl Rechtecke:").grid(row=0, column=0)
        self.entry_num_rectangles = tk.Entry(frame_inputs)
        self.entry_num_rectangles.grid(row=0, column=1)

        tk.Label(frame_inputs, text="Min Breite:").grid(row=1, column=0)
        self.entry_min_width = tk.Entry(frame_inputs)
        self.entry_min_width.grid(row=1, column=1)

        tk.Label(frame_inputs, text="Max Breite:").grid(row=2, column=0)
        self.entry_max_width = tk.Entry(frame_inputs)
        self.entry_max_width.grid(row=2, column=1)

        tk.Label(frame_inputs, text="Min Höhe:").grid(row=3, column=0)
        self.entry_min_height = tk.Entry(frame_inputs)
        self.entry_min_height.grid(row=3, column=1)

        tk.Label(frame_inputs, text="Max Höhe:").grid(row=4, column=0)
        self.entry_max_height = tk.Entry(frame_inputs)
        self.entry_max_height.grid(row=4, column=1)

        tk.Label(frame_inputs, text="Boxlänge L:").grid(row=5, column=0)
        self.entry_box_length = tk.Entry(frame_inputs)
        self.entry_box_length.grid(row=5, column=1)

        # Choose the selected algorithm
        self.algo_selector = ttk.Combobox(frame_inputs, values=["Greedy", "Lokale Suche"])
        self.algo_selector.set("Greedy")
        self.algo_selector.grid(row=6, column=1)

        # Choose Greedy strategy
        self.greedy_strat = ttk.Combobox(frame_inputs, values=["area", "aspect_ratio"])
        self.greedy_strat.set("area")
        self.greedy_strat.grid(row=7, column=1)
        self.greedy_strat.grid_remove()

        # Choose Local Search strategy
        self.local_search_neighborhood_selector = ttk.Combobox(frame_inputs, values=["Geometriebasiert", "Regelbasiert", "Überlappungen teilweise zulassen"])
        self.local_search_neighborhood_selector.set("Geometriebasiert")
        self.local_search_neighborhood_selector.grid(row=7, column=1)
        self.local_search_neighborhood_selector.grid_remove()

        # Maximum Iterations for Local Search
        self.local_search_max_iterations_label = tk.Label(frame_inputs, text="Maximum Iterationen")
        self.local_search_max_iterations_label.grid(row=8, column=0)
        self.local_search_max_iterations = tk.Entry(frame_inputs)
        self.local_search_max_iterations.grid(row=8, column=1)

        # Function to toggle visibility based on strategy
        self.algo_selector.bind("<<ComboboxSelected>>", self.update_algorithm)
        self.update_algorithm()

        # Label for error messages
        self.error_label = tk.Label(self.root, text="", fg="red")
        self.error_label.pack()

        # Create Buttons in UI to Generate Instances and Start Packer
        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(pady=10)

        btn_generate = tk.Button(frame_buttons, text="Instanz generieren", command=self.generate_rectangles)
        btn_generate.grid(row=0, column=0, padx=5)

        btn_run = tk.Button(frame_buttons, text="Algorithmus ausführen", command=self.run_algorithm)
        btn_run.grid(row=0, column=1, padx=5)

        btn_import = tk.Button(frame_buttons, text="Import Rechtecke", command=self.import_rectangles)
        btn_import.grid(row=1, column=0, padx=5)

        btn_export = tk.Button(frame_buttons, text="Export Rechtecke", command=self.export_rectangles)
        btn_export.grid(row=1, column=1, padx=5)

        # Display Status of Program and the canvas with the rectangles
        self.label_status = tk.Label(self.root, text="Status: Bereit")
        self.label_status.pack()

        # Create the scrollable canvas frame
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill="both", expand=True)

        # Create the canvas
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Add vertical scrollbar
        v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        v_scrollbar.pack(side="right", fill="y")

        # Configure the canvas to work with the vertical scrollbar
        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
    # Changes visibility for widgets based on the selected algorithm    
    def update_algorithm(self, *args):
        if self.algo_selector.get() == "Greedy":
            self.local_search_neighborhood_selector.grid_remove()
            self.local_search_max_iterations.grid_remove()
            self.local_search_max_iterations_label.grid_remove()
            self.local_search_max_iterations_is_visible = False
            self.greedy_strat.grid()
        elif self.algo_selector.get() == "Lokale Suche":
            self.greedy_strat.grid_remove()
            self.local_search_neighborhood_selector.grid()
            self.local_search_max_iterations.grid()
            self.local_search_max_iterations_label.grid()
            self.local_search_max_iterations_is_visible = True

    def validate_inputs(self):
        errors = []

        try:
            num_rectangles = int(self.entry_num_rectangles.get())
            min_width = int(self.entry_min_width.get())
            max_width = int(self.entry_max_width.get())
            min_height = int(self.entry_min_height.get())
            max_height = int(self.entry_max_height.get())
            box_length = int(self.entry_box_length.get())

            if num_rectangles < 1:
                errors.append("Es muss mind. 1 rechteck geben")
            if min_width > max_width:
                errors.append("Min Breite größer als Max Breite")
            if min_height > max_height:
                errors.append("Min Höhe größer als Max Höhe")
            if box_length < 1:
                errors.append("Die Länge der Box muss mind. 1 sein")
            if self.local_search_max_iterations_is_visible:
                max_iterations = int(self.local_search_max_iterations.get())
                if max_iterations < 1:
                    errors.append("Es muss mindestens eine Iteration ausgeführt werden")

        except ValueError:
            # Converting into ints fails
            errors.append("Bitte geben Sie gültige Zahlen ein und befüllen Sie alle Felder")

        return errors

    def generate_rectangles(self):
        self.error_label.config(text="")
        errors = self.validate_inputs()

        if errors:
            self.error_label.config(text="\n".join(errors), fg="red")
        else:
            n = int(self.entry_num_rectangles.get())
            min_w = int(self.entry_min_width.get())
            max_w = int(self.entry_max_width.get())
            min_h = int(self.entry_min_height.get())
            max_h = int(self.entry_max_height.get())
            self.L = int(self.entry_box_length.get())

            self.rectangles = self.generate_instances(n, min_w, max_w, min_h, max_h)
            self.label_status.config(text=f"{n} Rechtecke generiert!")
        
    def run_algorithm(self):
        algorithm = self.algo_selector.get()
        if algorithm == "Greedy":
            solution = self.greedy_algorithm(
                self.rectangles, 
                self.L, 
                self.greedy_strat.get()
            )
        elif algorithm == "Lokale Suche":
            solution = self.local_search(
                self.rectangles, 
                self.L, 
                self.local_search_neighborhood_selector.get(),
                int(self.local_search_max_iterations.get())
            )
        self.visualize_solution(solution)

    def visualize_solution(self, solution):
        self.canvas.delete("all")

        box_padding = 10
        x_offset = 0
        y_offset = 0
        row_height = 0
        canvas_width = self.canvas.winfo_width()

        for box_id, box in enumerate(solution):
            if x_offset + self.L + box_padding > canvas_width:
                x_offset = 0
                y_offset += row_height + box_padding
                row_height = 0

            row_height = max(row_height, self.L)

            self.canvas.create_rectangle(
                x_offset, y_offset,
                x_offset + self.L, y_offset + self.L,
                outline="black"
            )

            for rect in box:
                x, y, w, h = rect
                self.canvas.create_rectangle(
                    x_offset + x, y_offset + y,
                    x_offset + x + w, y_offset + y + h,
                    fill=random.choice(["red", "green", "blue", "yellow"]),
                    outline="black"
                )

            x_offset += self.L + box_padding

        self.update_scrollregion()
        
    def update_scrollregion(self):
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def import_rectangles(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    data = json.load(file)
                    
                    # Populate rectangles and box length
                    self.rectangles = data.get("rectangles", [])
                    self.L = data.get("box_length", 0)
                    
                    # Update input fields
                    self.entry_num_rectangles.delete(0, tk.END)
                    self.entry_num_rectangles.insert(0, data.get("num_rectangles", ""))
                    
                    self.entry_min_width.delete(0, tk.END)
                    self.entry_min_width.insert(0, data.get("min_width", ""))
                    
                    self.entry_max_width.delete(0, tk.END)
                    self.entry_max_width.insert(0, data.get("max_width", ""))
                    
                    self.entry_min_height.delete(0, tk.END)
                    self.entry_min_height.insert(0, data.get("min_height", ""))
                    
                    self.entry_max_height.delete(0, tk.END)
                    self.entry_max_height.insert(0, data.get("max_height", ""))
                    
                    self.entry_box_length.delete(0, tk.END)
                    self.entry_box_length.insert(0, self.L)
                    
                    self.label_status.config(text="Rechtecke erfolgreich importiert!")
            except Exception as e:
                self.error_label.config(text=f"Fehler beim Importieren: {e}", fg="red")
    
    def export_rectangles(self):
        default_filename = "rectangles.json"
        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            try:
                with open(file_path, "w") as file:
                    data = {
                        "rectangles": self.rectangles,
                        "box_length": self.L,
                        "num_rectangles": len(self.rectangles),
                        "min_width": self.entry_min_width.get(),
                        "max_width": self.entry_max_width.get(),
                        "min_height": self.entry_min_height.get(),
                        "max_height": self.entry_max_height.get(),
                    }
                    json.dump(data, file)
                    self.label_status.config(text="Rechtecke erfolgreich exportiert!")
            except Exception as e:
                self.error_label.config(text=f"Fehler beim Exportieren: {e}", fg="red")