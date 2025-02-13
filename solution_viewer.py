import json
import tkinter as tk
from tkinter import filedialog
import random

from objects import Box, RecPac_Solution, Rectangle

class SolutionViewer:
    def __init__(self, root, solutions):
        self.root = root
        self.solutionsRaw = solutions
        self.solutions = []
        self.solutionsalgorithms = []
        self.rectangle_colors = {}
        self.current_type = "greedy"  # Start with Greedy solutions
        self.current_index = 0
        self.zoom_factor = 1.0
        self.zoom_steps = 0
        self.max_zoom_steps = 4
        
        self.parse_solutions()
        self.setup_ui()
        self.visualize_solution()
    
    def parse_solutions(self):
        
        solutionsRaw = self.solutionsRaw["solutions"]
        box_length = int(self.solutionsRaw["box_length"])
        
        for solution in solutionsRaw:
            current_solution = RecPac_Solution()
            for box in solution["boxes"]:
                current_box = Box(box_length)
                for rectangle in box:
                    current_box.add_rectangle(Rectangle(rectangle["x"], rectangle["y"], rectangle["w"], rectangle["h"]))
                current_solution.add_box(current_box)
            self.solutions.append(current_solution)
            self.solutionsalgorithms.append(solution["algorithm"])
    
    def setup_ui(self):
        self.root.title("Optimierungsalgorithmen GUI")

        # Create input fields and place them in UI
        frame_inputs = tk.Frame(self.root)
        frame_inputs.pack(pady=10)

        # Create Buttons in UI to Generate Instances and Start Packer
        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(pady=10)

        btn_zoom_in = tk.Button(frame_buttons, text="Zoom In", command=self.zoom_in)
        btn_zoom_in.grid(row=0, column=2, padx=5)
        
        btn_zoom_out = tk.Button(frame_buttons, text="Zoom Out", command=self.zoom_out)
        btn_zoom_out.grid(row=0, column=3, padx=5)
        
        btn_iterate_left = tk.Button(frame_buttons, text="<", command=self.lower_solution_index)
        btn_iterate_left.grid(row=1, column=2, padx=5)
        
        btn_iterate_right = tk.Button(frame_buttons, text=">", command=self.increase_solution_index)
        btn_iterate_right.grid(row=1, column=3, padx=5)
        
        self.label_solution_type = tk.Label(self.root, text=f"Solution of {self.solutionsalgorithms[self.current_index]} algorithm")
        self.label_solution_type.pack()
        
        self.label_solution_number = tk.Label(self.root, text=f"Solution: {self.current_index+1}/{len(self.solutions)}")
        self.label_solution_number.pack()

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
        
    def lower_solution_index(self):
        if(self.current_index > 0):
            self.current_index -= 1
            self.label_solution_type.config(text=f"Solution of {self.solutionsalgorithms[self.current_index]} algorithm")
            self.label_solution_number.config(text=f"Solution: {self.current_index+1}/{len(self.solutions)}")
            self.redraw_canvas()
    
    def increase_solution_index(self):
        if(self.current_index < len(self.solutions)-1):
            self.current_index += 1
            self.label_solution_type.config(text=f"Solution of {self.solutionsalgorithms[self.current_index]} algorithm")
            self.label_solution_number.config(text=f"Solution: {self.current_index+1}/{len(self.solutions)}")
            self.redraw_canvas()
        
    def get_rectangle_color(self, rect):
        if len(self.rectangle_colors.keys()) == 0 or rect not in self.rectangle_colors.keys():
            color = random.choice(["red", "green", "blue", "yellow", "purple", "orange", "cyan"])
            self.rectangle_colors[rect] = color
        else:
            color = self.rectangle_colors[rect]
        return color

    def update_scrollregion(self):
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def visualize_solution(self):
        self.canvas.delete("all")

        box_padding = 10 * self.zoom_factor  # Skaliere den Abstand zwischen den Boxen
        x_offset = 0
        y_offset = 0
        row_height = 0
        canvas_width = self.canvas.winfo_width()
        
        length = self.solutions[self.current_index].boxes[0].box_length

        for box_id, box in enumerate(self.solutions[self.current_index].boxes):
            scaled_box_length = int(length * self.zoom_factor)

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

        self.update_scrollregion()
    
    def zoom_in(self):
        if self.zoom_steps < self.max_zoom_steps:
            self.zoom_factor *= 1.2
            self.zoom_steps += 1
            self.redraw_canvas()
    
    def redraw_canvas(self):
        self.canvas.delete("all")
        self.visualize_solution() 
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
    def zoom_out(self):
        if self.zoom_steps > -1:
            self.zoom_factor /= 1.2
            self.zoom_steps -= 1
            self.redraw_canvas()
    
    @staticmethod
    def load_solutions():
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r") as file:
                return json.load(file)
        return {}
    
if __name__ == "__main__":
    root = tk.Tk()
    solutions = SolutionViewer.load_solutions()
    app = SolutionViewer(root, solutions)
    root.mainloop()
