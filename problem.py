from abc import ABC, abstractmethod

class OptimizationProblem(ABC):

    @abstractmethod
    def start_solution(self):
        pass

    @abstractmethod
    def evaluate_solution(self, solution):
        pass

    @abstractmethod
    def generate_neighbors(self, solution):
        pass

    @abstractmethod
    def is_better(self, solution1, solution2):
        pass

class RectanglePacker(OptimizationProblem):
    
    def __init__(self, rectangles, box_length, neighborhood_strategy):
        self.rectangles = rectangles
        self.box_length = box_length
        self.neighborhood_strategy = neighborhood_strategy

    def start_solution(self):
        return [[rect] for rect in self.rectangles]
    
    def evaluate_solution(self, solution):
        return len(solution)
    
    def generate_neighbors(self, solution):
        return self.neighborhood_strategy.generate_neighbors(solution, self)

    def is_better(self, solution1, solution2):
        return self.evaluate_solution(solution1) <= self.evaluate_solution(solution2)