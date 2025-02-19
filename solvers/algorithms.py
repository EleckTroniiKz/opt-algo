import cProfile
import math
import random
import time
import sys

from classes.base_classes import OptimizationProblem, Solution, Neighborhood
import classes.helpers
from classes.rectangle_packer_types import RecPac_Solution

class Greedy:
    def __init__(self, problem: OptimizationProblem, solution_type: type, strategy="largest_area_first"):
        self.problem = problem
        self.solution_type = solution_type
        self.problem.items = classes.helpers.apply_greedy_strategy(self.problem.items, strategy)

    def solve(self):
        start_time = time.time()

        current_solution = self.solution_type()
        for item in self.problem.items:
            new_solution = self.problem.add_to_solution(current_solution, item)
            if new_solution is not None:
                current_solution = new_solution

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Laufzeit Greedy: {elapsed_time:.6f} Sekunden")

        return current_solution


class LocalSearch:
    def __init__(self, problem: OptimizationProblem, start_solution: Solution, max_iterations: int,
                 neighborhood: Neighborhood):
        self.problem = problem
        self.start_solution = start_solution
        self.max_iterations = max_iterations
        self.neighborhood = neighborhood

    def solve(self):
        start_time = time.time()

        current_solution = self.start_solution
        best_solution = current_solution
        best_value = best_solution.evaluate_solution()
        iteration = 0

        profiler = cProfile.Profile()
        profiler.enable()  # Profiling starten

        while iteration < self.max_iterations:
            neighbor = self.neighborhood.generate_neighbor(current_solution)
            neighbor_value = neighbor.evaluate_solution()

            if neighbor_value <= best_value:
                current_solution = neighbor
                best_solution = neighbor
                best_value = neighbor_value

            iteration += 1

        profiler.disable()  # Profiling stoppen
        profiler.print_stats(sort="tottime")  # Ergebnisse ausgeben

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Laufzeit LocalSearch: {elapsed_time:.6f} Sekunden")

        return best_solution


class SimulatedAnnealing:
    def __init__(self, problem: OptimizationProblem, start_solution: RecPac_Solution,
                 initial_temperature: float, end_temperature: float, cooling_rate: float,
                 iterations_per_temp: int, neighborhood_strategy: Neighborhood):
        self.problem = problem
        self.start_solution = start_solution
        self.initial_temperature = initial_temperature
        self.end_temperature = end_temperature
        self.cooling_rate = cooling_rate
        self.iterations_per_temp = iterations_per_temp
        self.neighborhood_strategy = neighborhood_strategy

    def solve(self):
        start_time = time.time()

        current_solution = self.start_solution
        best_solution = current_solution
        best_value = best_solution.evaluate_solution()
        temperature = self.initial_temperature

        while temperature > self.end_temperature:
            for _ in range(self.iterations_per_temp):
                neighbor = self.neighborhood_strategy.generate_neighbor(current_solution)
                neighbor_value = neighbor.evaluate_solution()

                delta = neighbor_value - best_value

                if delta < 0 or random.uniform(0, 1) < math.exp(-delta / temperature):
                    current_solution = neighbor
                    if neighbor_value < best_value:
                        best_solution = neighbor
                        best_value = neighbor_value

            temperature *= self.cooling_rate

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Laufzeit Simulated Annealing: {elapsed_time:.6f} Sekunden")

        return best_solution


class Backtracking:
    def __init__(self, problem: OptimizationProblem, solution_type: type):
        self.problem = problem
        self.solution_type = solution_type
        sys.setrecursionlimit(10 ** 6)

    def solve(self):
        start_time = time.time()

        current_solution = self.solution_type()

        result = self._backtrack(current_solution, 0)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Laufzeit Backtracking: {elapsed_time:.6f} Sekunden")

        return result

    def _backtrack(self, current_solution: Solution, index: int):
        if index >= len(self.problem.items):
            return current_solution

        item = self.problem.items[index]

        new_solution = self.problem.add_to_solution(current_solution, item)

        if new_solution is not None:
            result = self._backtrack(new_solution, index + 1)
            if result is not None:
                return result

        return None
