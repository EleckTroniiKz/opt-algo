from problem import OptimizationProblem

class Greedy:
    def __init__(self, problem: OptimizationProblem, strategy):
        self.problem = problem
        self.strategy = strategy
    
    def solve(self):
        current_solution = self.problem.start_solution()
        best_solution = current_solution
        best_value = self.problem.evaluate_solution(best_solution)

        while True:
            neighbors = self.problem.generate_neighbors(current_solution)
            best_neighbor = None
            best_neighbor_value = best_value

            for neighbor in neighbors:
                neighbor_value = self.problem.evaluate_solution(neighbor)
                if neighbor_value > best_neighbor_value:
                    best_neighbor = neighbor
                    best_neighbor_value = neighbor_value

            if best_neighbor is None:
                break

            current_solution = best_neighbor
            if best_neighbor_value > best_value:
                best_solution = best_neighbor
                best_value = best_neighbor_value

        return best_solution

class LocalSearch:
    
    def __init__(self, problem, neighborhood):
        self.problem = problem
        self.neighborhood = neighborhood
        
    def solve(self):
        current_solution = self.problem.start_solution()
        best_solution = current_solution
        best_value = self.problem.evaluate_solution(best_solution)

        while True:
            neighbors = self.problem.generate_neighbors(current_solution)
            improved = False
            for neighbor in neighbors:
                neighbor_value = self.problem.evaluate_solution(neighbor)
                if neighbor_value > best_value:
                    current_solution = neighbor
                    best_solution = neighbor
                    best_value = neighbor_value
                    improved = True
                    break

            if not improved:
                break

        return best_solution

class SimmulatedAnnealing:
    pass

class Backtracking:
    pass