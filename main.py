import tkinter as tk
from strategy import apply_strategy
from view import GUI
from neighborhoods import GeometryBasedStrategy, RuleBasedStrategy, OverlapStrategy
from problem import RectanglePacker
from algorithms import Greedy, LocalSearch

def main():

    def greedy_algorithm(rectangles, box_length, strategy_name):
        rectangles = apply_strategy(rectangles, strategy_name)
        problem = RectanglePacker(rectangles, box_length)
        greedy_solver = Greedy(problem, strategy_name)
        return greedy_solver.solve()

    def local_search_algorithm(rectangles, box_length, neighborhood_name, max_iterations):
        neighborhood_map = {
            "Geometriebasiert": GeometryBasedStrategy(),
            "Regelbasiert": RuleBasedStrategy(),
            "Überlappungen teilweise zulassen": OverlapStrategy(initial_overlap=0.1)
        }
        problem = RectanglePacker(rectangles, box_length)
        local_search_solver = LocalSearch(problem, max_iterations, neighborhood_map[neighborhood_name])
        return local_search_solver.solve()

    root = tk.Tk()
    app = GUI(root, greedy_algorithm, local_search_algorithm)
    root.mainloop()

if __name__ == "__main__":
    main()
