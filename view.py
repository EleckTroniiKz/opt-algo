import tkinter as tk
from tkinter import ttk, filedialog
import random
from typing import List
from helpers import generate_instances
from objects import Rectangle
from PIL import Image, ImageTk
import json

class Tooltip:
        def __init__(self, widget, text):
            self.widget = widget
            self.text = text
            self.tooltip_window = None
            self.widget.bind("<Enter>", self.show_tooltip)
            self.widget.bind("<Leave>", self.hide_tooltip)

        def show_tooltip(self, event):
            """Display the tooltip near the widget."""
            x, y, _, _ = self.widget.bbox("insert")  # Get widget position
            x += self.widget.winfo_rootx() + 25  # Offset for better placement
            y += self.widget.winfo_rooty() + 25

            self.tooltip_window = tk.Toplevel(self.widget)
            self.tooltip_window.wm_overrideredirect(True)  # Remove window border
            self.tooltip_window.geometry(f"+{x}+{y}")  # Position the tooltip

            label = tk.Label(self.tooltip_window, text=self.text, bg="lightyellow", relief="solid", borderwidth=1, padx=5, pady=2)
            label.pack()

        def hide_tooltip(self, event):
            """Destroy the tooltip window when mouse leaves."""
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None


class GUI:
    
    def __init__(self, root, greedy_algorithm, local_search):
        self.root = root
        self.greedy_algorithm = greedy_algorithm
        self.local_search = local_search
        self.current_solution = None
        self.can_export_rectangles = "disabled"
        self.can_zoom = "disabled"
        
        self.instances: List[Rectangle] = []
        self.box_size: int = 0
        
        self.rectangle_colors = {}
        
        self.zoom_factor = 1.0
        self.zoom_steps = 0
        self.max_zoom_steps = 4
        
        self.setup_ui()
    
    def setup_ui(self):
        self.root.title("Optimierungsalgorithmen GUI")
        
        self.zoom_in_icon = Image.open("assets/zoom-in.png").resize((30, 30))
        self.zoom_in_icon = ImageTk.PhotoImage(self.zoom_in_icon)
        self.zoom_out_icon = Image.open("assets/zoom-out.png").resize((30, 30))
        self.zoom_out_icon = ImageTk.PhotoImage(self.zoom_out_icon)
        self.import_icon = Image.open("assets/import.png").resize((30, 30))
        self.import_icon = ImageTk.PhotoImage(self.import_icon)
        self.export_icon = Image.open("assets/export.png").resize((30, 30))
        self.export_icon = ImageTk.PhotoImage(self.export_icon)

        # Create input fields and place them in UI
        frame_inputs = tk.Frame(self.root)
        frame_inputs.pack(pady=10)

        tk.Label(frame_inputs, text="Anzahl Rechtecke:").grid(row=0, column=0)
        self.entry_num_rectangles = tk.Entry(frame_inputs)
        self.entry_num_rectangles.grid(row=0, column=1, pady=5)

        tk.Label(frame_inputs, text="Min Breite:").grid(row=1, column=0)
        self.entry_min_width = tk.Entry(frame_inputs)
        self.entry_min_width.grid(row=1, column=1, pady=5)

        tk.Label(frame_inputs, text="Max Breite:").grid(row=2, column=0)
        self.entry_max_width = tk.Entry(frame_inputs)
        self.entry_max_width.grid(row=2, column=1, pady=5)

        tk.Label(frame_inputs, text="Min Höhe:").grid(row=3, column=0)
        self.entry_min_height = tk.Entry(frame_inputs)
        self.entry_min_height.grid(row=3, column=1, pady=5)

        tk.Label(frame_inputs, text="Max Höhe:").grid(row=4, column=0)
        self.entry_max_height = tk.Entry(frame_inputs)
        self.entry_max_height.grid(row=4, column=1, pady=5)

        tk.Label(frame_inputs, text="Boxlänge L:").grid(row=5, column=0)
        self.entry_box_length = tk.Entry(frame_inputs)
        self.entry_box_length.grid(row=5, column=1, pady=5)

        # Choose the selected algorithm
        self.algo_select_label = tk.Label(frame_inputs, text="Algorithmus wählen: ").grid(row=7, column=0, padx=5)
        self.algo_selector = ttk.Combobox(frame_inputs, values=["Greedy", "Lokale Suche"], state="readonly")
        self.algo_selector.set("Greedy")
        self.algo_selector.grid(row=7, column=1, pady=5)

        # Choose Greedy strategy
        self.strategy_label = ttk.Label(frame_inputs, text="Greedy Strategie wählen: ")
        self.strategy_label.grid(row=8, column=0, padx=5)
        self.greedy_strat = ttk.Combobox(frame_inputs, state="readonly", values=["Größte Fläche zuerst", "Kleinste Fläche zuerst", "Größtes Seitenverhältnis zuerst", "Kleinstes Seitenverhältnis zuerst"])
        self.greedy_strat.set("Größte Fläche zuerst")
        self.greedy_strat.grid(row=8, column=1)
        self.greedy_strat.grid_remove()
        self.strategy_label.grid_remove()

        # Choose Local Search strategy
        self.neighborhood_label = ttk.Label(frame_inputs, text="Nachbarschaft wählen")
        self.neighborhood_label.grid(row=9, column=0, padx=5)
        self.local_search_neighborhood_selector = ttk.Combobox(frame_inputs, values=["Geometriebasiert", "Regelbasiert", "Überlappungen teilweise zulassen"])
        self.local_search_neighborhood_selector.set("Geometriebasiert")
        self.local_search_neighborhood_selector.grid(row=9, column=1)
        self.local_search_neighborhood_selector.grid_remove()
        self.neighborhood_label.grid_remove()

        # Maximum Iterations for Local Search
        self.local_search_max_iterations_label = tk.Label(frame_inputs, text="Maximum Iterationen")
        self.local_search_max_iterations_label.grid(row=10, column=0, pady=5)
        self.local_search_max_iterations = tk.Entry(frame_inputs)
        self.local_search_max_iterations.grid(row=10, column=1)

        # Function to toggle visibility based on strategy
        self.algo_selector.bind("<<ComboboxSelected>>", self.update_algorithm)
        self.update_algorithm()

        # Label for error messages
        self.error_label = tk.Label(self.root, text="", fg="red")
        self.error_label.pack()

        # Create Buttons in UI to Generate Instances and Start Packer
        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(pady=10)

        btn_generate = tk.Button(frame_buttons, text="Rechtecke generieren", command=self.generate_rectangles_clicked)
        btn_generate.grid(row=0, column=0, padx=5)

        btn_run = tk.Button(frame_buttons, text="Algorithmus ausführen", command=self.run_algorithm)
        btn_run.grid(row=1, column=0, padx=5)
        
        self.btn_import = tk.Button(frame_buttons, image=self.import_icon, width=30, borderwidth=0,command=self.import_rectangles)
        self.btn_import.grid(row=1, column=1, padx=5)
        Tooltip(self.btn_import, "Importiere Rechtecke")

        self.btn_export = tk.Button(frame_buttons, image=self.export_icon, width=30, borderwidth=0, state="disabled",command=self.export_rectangles)
        self.btn_export.grid(row=1, column=2, padx=5)
        Tooltip(self.btn_export, "Exportiere Rechtecke")

        self.btn_zoom_in = tk.Button(frame_buttons, image=self.zoom_in_icon, borderwidth=0, state="disabled", command=self.zoom_in)
        self.btn_zoom_in.grid(row=1, column=3, padx=5)
        Tooltip(self.btn_zoom_in, "Zoom In")
        
        self.btn_zoom_out = tk.Button(frame_buttons, image=self.zoom_out_icon, borderwidth=0, state="disabled",command=self.zoom_out)
        self.btn_zoom_out.grid(row=1, column=4, padx=5)
        Tooltip(self.btn_zoom_out, "Zoome Out")

        

        # Display Status of Program and the canvas with the rectangles
        self.label_status = tk.Label(self.root, text="Status: Bereit")
        self.label_status.pack()

        # Create the scrollable canvas frame
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill="both", expand=True)

        # Create the canvas
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # Add vertical scrollbar
        v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        v_scrollbar.pack(side="right", fill="y")

        # Configure the canvas to work with the vertical scrollbar
        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
        
    def zoom_in(self):
        if(self.zoom_steps < 10):
            self.btn_zoom_in.config(state="normal")
            self.zoom_factor *= 1.2
            self.zoom_steps += 1
            self.redraw_canvas()
        else:
            self.btn_zoom_in.config(state="disabled")
        
    def zoom_out(self):
        if(self.zoom_steps > -1):
            self.btn_zoom_out.config(state="normal")
            self.zoom_factor /= 1.2
            self.zoom_steps -= 1
            self.redraw_canvas()
        else:
            self.btn_zoom_out.config(state="disabled")
        
    def redraw_canvas(self):
        self.canvas.delete("all")
        self.visualize_solution(self.current_solution)
        
        
    # Changes visibility for widgets based on the selected algorithm    
    def update_algorithm(self, *args):
        if self.algo_selector.get() == "Greedy":
            self.local_search_neighborhood_selector.grid_remove()
            self.local_search_max_iterations.grid_remove()
            self.local_search_max_iterations_label.grid_remove()
            self.neighborhood_label.grid_remove()
            self.local_search_max_iterations_is_visible = False
            self.strategy_label.grid()
            self.greedy_strat.grid()
        elif self.algo_selector.get() == "Lokale Suche":
            self.greedy_strat.grid_remove()
            self.local_search_neighborhood_selector.grid()
            self.strategy_label.grid_remove()
            self.local_search_max_iterations.grid()
            self.local_search_max_iterations_label.grid()
            self.neighborhood_label.grid()
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
            if min_width > box_length or max_width > box_length or min_height > box_length or max_height > box_length:
                errors.append("Die Rechtecke dürfen nicht breiter/höher sein als die Box")
            if self.local_search_max_iterations_is_visible:
                max_iterations = int(self.local_search_max_iterations.get())
                if max_iterations < 1:
                    errors.append("Es muss mindestens eine Iteration ausgeführt werden")

        except ValueError:
            # Converting into ints fails
            errors.append("Bitte geben Sie gültige Zahlen ein und befüllen Sie alle Felder")

        return errors

    def generate_rectangles_clicked(self):
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
            self.box_size = int(self.entry_box_length.get())

            self.instances = generate_instances(n, min_w, max_w, min_h, max_h)
            self.btn_export.config(state="normal")
            self.label_status.config(text=f"{n} Rechtecke generiert!")
        
    def run_algorithm(self):
        algorithm = self.algo_selector.get()
        self.zoom_factor = 1.2
        self.zoom_steps = 0
        self.rectangle_colors = {}
        if algorithm == "Greedy":
            solution = self.greedy_algorithm(
                self.instances, 
                self.box_size, 
                self.greedy_strat.get()
            )
        elif algorithm == "Lokale Suche":
            solution = self.local_search(
                self.instances, 
                self.box_size, 
                self.local_search_neighborhood_selector.get(),
                int(self.local_search_max_iterations.get())
            )
        self.current_solution = solution
        self.visualize_solution(solution)

    def get_rectangle_color(self, rect):
        if len(self.rectangle_colors.keys()) == 0 or rect not in self.rectangle_colors.keys():
            color = random.choice(["red", "green", "blue", "yellow", "purple", "orange", "cyan"])
            self.rectangle_colors[rect] = color
        else:
            color = self.rectangle_colors[rect]
        return color

    def visualize_solution(self, solution):
        self.canvas.delete("all")

        box_padding = 10 * self.zoom_factor  # Skaliere den Abstand zwischen den Boxen
        x_offset = 0
        y_offset = 0
        row_height = 0
        canvas_width = self.canvas.winfo_width()

        for box_id, box in enumerate(solution.boxes):
            scaled_box_length = int(self.box_size * self.zoom_factor)

            # Überprüfen, ob die Box in die aktuelle Zeile passt
            if x_offset + scaled_box_length + box_padding > canvas_width:
                x_offset = 0
                y_offset += row_height + box_padding
                row_height = 0

            row_height = max(row_height, scaled_box_length)

            # Zeichne die Box
            self.canvas.create_rectangle(
                x_offset, y_offset,
                x_offset + scaled_box_length, y_offset + scaled_box_length,
                outline="black"
            )

            # Zeichne die Rechtecke innerhalb der Box
            for rect in box.rectangles:
                x, y, w, h = rect.x, rect.y, rect.width, rect.height
                scaled_x = int(x * self.zoom_factor) + x_offset
                scaled_y = int(y * self.zoom_factor) + y_offset
                scaled_w = int(w * self.zoom_factor)
                scaled_h = int(h * self.zoom_factor)

                self.canvas.create_rectangle(
                    scaled_x, scaled_y,
                    scaled_x + scaled_w, scaled_y + scaled_h,
                    fill=self.get_rectangle_color(rect),
                    outline="black"
                )

            # Aktualisiere den x_offset für die nächste Box
            x_offset += scaled_box_length + box_padding
        self.btn_zoom_in.config(state="normal")
        self.btn_zoom_out.config(state="normal")
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
                    self.instances = [Rectangle(rect[0], rect[1], rect[2], rect[3]) for rect in data.get("rectangles", [])]
                    self.box_size = data.get("box_length", 0)
                    
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
                    self.entry_box_length.insert(0, self.box_size)
                    
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
                        "rectangles": [(instance.x, instance.y, instance.width, instance.height) for instance in self.instances],
                        "box_length": self.box_size,
                        "num_rectangles": len(self.instances),
                        "min_width": self.entry_min_width.get(),
                        "max_width": self.entry_max_width.get(),
                        "min_height": self.entry_min_height.get(),
                        "max_height": self.entry_max_height.get(),
                    }
                    json.dump(data, file)
                    self.label_status.config(text="Rechtecke erfolgreich exportiert!")
            except Exception as e:
                self.error_label.config(text=f"Fehler beim Exportieren: {e}", fg="red")