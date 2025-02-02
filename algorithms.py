from neighborhoods import NeighborhoodStrategy
from objects import RecPac_Solution
from problem import OptimizationProblem


class Greedy:
    def __init__(self, problem: OptimizationProblem, strategy="largest_area_first"):
        self.problem = problem
        self.strategy = strategy

    def solve(self):
        current_solution = RecPac_Solution()  # Start with an empty solution
        best_value = current_solution.evaluate_solution()
        # Iterate over all instances and place each one
        for instance in self.problem.rectangles:
            new_solution = self.problem.add_to_solution(current_solution, instance)
            if new_solution is not None:
                current_solution = new_solution

        return current_solution


class LocalSearch:
    def __init__(self, problem: OptimizationProblem, start_solution: RecPac_Solution, max_iterations: int,
                 neighborhood_strategy: NeighborhoodStrategy, initial_temperature: float = 100.0):
        self.problem = problem
        self.start_solution = start_solution
        self.max_iterations = max_iterations
        self.neighborhood_strategy = neighborhood_strategy
        self.temperature = initial_temperature

    def solve(self):
        current_solution = self.start_solution
        best_solution = current_solution
        best_value = best_solution.evaluate_solution()
        iteration = 0
        stagnation = 0

        while iteration < self.max_iterations:
            # Generate a single neighbor (adjust to match your strategy's behavior)
            neighbor = self.neighborhood_strategy.generate_neighbor(current_solution, self.temperature)
            neighbor_value = neighbor.evaluate_solution()

            # Accept better solution directly, worse solution with probability
            if neighbor_value > best_value:
                current_solution = neighbor
                best_solution = neighbor
                best_value = neighbor_value
                stagnation = 0
            else:
                stagnation += 1

            if stagnation > self.max_iterations / 10:
                return best_solution

            iteration += 1

        return best_solution


class SimmulatedAnnealing:
    pass


class Backtracking:
    pass
