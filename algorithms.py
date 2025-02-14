import time
import sys
from neighborhoods import NeighborhoodStrategy
from objects import RecPac_Solution
from problem import OptimizationProblem


class Greedy:
    def __init__(self, problem: OptimizationProblem, strategy="largest_area_first"):
        self.problem = problem
        self.strategy = strategy

    def solve(self):
        start_time = time.time()

        current_solution = RecPac_Solution() # Start with an empty solution
        # Iterate over all instances and place each one
        for instance in self.problem.rectangles:
            new_solution = self.problem.add_to_solution(current_solution, instance)
            if new_solution is not None:
                current_solution = new_solution

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Laufzeit Greedy: {elapsed_time:.6f} Sekunden")

        return current_solution


class LocalSearch:
    def __init__(self, problem: OptimizationProblem, start_solution: RecPac_Solution, max_iterations: int,
                 neighborhood_strategy: NeighborhoodStrategy):
        self.problem = problem
        self.start_solution = start_solution
        self.max_iterations = max_iterations
        self.neighborhood_strategy = neighborhood_strategy

    def solve(self):
        start_time = time.time()

        current_solution = self.start_solution
        best_solution = current_solution
        best_value = best_solution.evaluate_solution()
        iteration = 0

        while iteration < self.max_iterations:
            # Generate a single neighbor (adjust to match your strategy's behavior)
            neighbor = self.neighborhood_strategy.generate_neighbor(current_solution)
            neighbor_value = neighbor.evaluate_solution()
            if neighbor_value <= best_value:
                current_solution = neighbor
                best_solution = neighbor
                best_value = neighbor_value

            iteration += 1

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Laufzeit LocalSearch: {elapsed_time:.6f} Sekunden")

        return best_solution


class SimmulatedAnnealing:
    pass


class Backtracking:
    def __init__(self, problem: OptimizationProblem):
        self.problem = problem
        sys.setrecursionlimit(10**6)

    def solve(self):
        start_time = time.time()

        # Initialize an empty solution
        current_solution = RecPac_Solution()

        # Start the backtracking process
        result = self._backtrack(current_solution, 0)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Laufzeit Backtracking: {elapsed_time:.6f} Sekunden")

        return result

    def solve(self):
        start_time = time.time()

        # Initialize an empty solution
        current_solution = RecPac_Solution()

        # Start the backtracking process
        result = self._backtrack(current_solution, 0)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Laufzeit Backtracking: {elapsed_time:.6f} Sekunden")

        return result

    def _backtrack(self, current_solution: RecPac_Solution, index: int):
        # Wenn alle Rechtecke platziert sind, return
        if index >= len(self.problem.rectangles):
            return current_solution

        # aktuelles Rechteck zum platzieren
        rectangle = self.problem.rectangles[index]

        # Platziere Rechteck in Lösung
        new_solution = self.problem.add_to_solution(current_solution, rectangle)

        if new_solution is not None:
            # Wenn neue Lösung None ist, versuche rekursiv weiter
            result = self._backtrack(new_solution, index + 1)
            if result is not None:
                return result

        # If no valid placement is found even after rotation, backtrack
        return None
