import tkinter as tk
from view import GUI
from neighborhoods import GeometryBasedStrategy, RuleBasedStrategy, OverlapStrategy
from problem import RectanglePacker
from algorithms import Greedy, LocalSearch
from helpers import generate_instances

def main():

    def greedy_algorithm(rectangles, box_length, strategy_name):
        strategy_map = {
            "area": "area",  # Add appropriate strategy configurations if needed
            "aspect_ratio": "aspect_ratio"
        }
        problem = RectanglePacker(rectangles, box_length, GeometryBasedStrategy())
        greedy_solver = Greedy(problem, strategy_map[strategy_name])
        return greedy_solver.solve()

    def local_search_algorithm(rectangles, box_length, neighborhood_name):
        neighborhood_map = {
            "Geometriebasiert": GeometryBasedStrategy(),
            "Regelbasiert": RuleBasedStrategy(),
            "Überlappungen teilweise zulassen": OverlapStrategy(initial_overlap=0.1)
        }
        problem = RectanglePacker(rectangles, box_length, neighborhood_map[neighborhood_name])
        local_search_solver = LocalSearch(problem, neighborhood_map[neighborhood_name])
        return local_search_solver.solve()

    root = tk.Tk()
    app = GUI(root, generate_instances, greedy_algorithm, local_search_algorithm)
    root.mainloop()

if __name__ == "__main__":
    main()
