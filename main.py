import tkinter as tk
import random

from algorithms import Greedy, LocalSearch, Backtracking
from neighborhoods import GeometryBasedStrategy, RuleBasedStrategy, OverlapStrategy
from objects import RecPac_Solution, Box
from problem import RectanglePacker
from strategy import apply_strategy
from view import GUI


def main():
    def greedy_algorithm(rectangles, box_length, strategy_name):
        rectangles = apply_strategy(rectangles, strategy_name)
        problem = RectanglePacker(rectangles, box_length)
        greedy_solver = Greedy(problem, strategy_name)
        return greedy_solver.solve()

    def local_search_algorithm(rectangles, box_length, neighborhood_name, max_iterations):
        start_solution_map = {
            "Geometriebasiert": generate_bad_solution(rectangles, box_length),
            "Regelbasiert": greedy_algorithm(rectangles, box_length, "Größte Fläche zuerst"),
        }
        problem = RectanglePacker(rectangles, box_length)
        neighborhood_map = {
            "Geometriebasiert": GeometryBasedStrategy(problem),
            "Regelbasiert": RuleBasedStrategy(problem),
            "Überlappungen teilweise zulassen": OverlapStrategy(initial_overlap=0.1)
        }
        local_search_solver = LocalSearch(problem, start_solution_map[neighborhood_name], max_iterations, neighborhood_map[neighborhood_name])
        return local_search_solver.solve()

    def backtracking_algorithm(rectangles, box_length):
        problem = RectanglePacker(rectangles, box_length)
        backtracking_solver = Backtracking(problem)
        solution = backtracking_solver.solve()
        return solution

    def generate_bad_solution(rectangles, box_length):
        bad_solution = RecPac_Solution()

        for rect in rectangles:
            new_box = Box(box_length)

            if random.random() < 0.5:
                rect.width, rect.height = rect.height, rect.width

            rect.x = random.randint(0, box_length - rect.width)
            rect.y = random.randint(0, box_length - rect.height)

            new_box.add_rectangle(rect)
            bad_solution.add_box(new_box)
        return bad_solution

    root = tk.Tk()
    app = GUI(root, greedy_algorithm, local_search_algorithm, backtracking_algorithm)
    root.mainloop()


if __name__ == "__main__":
    main()
