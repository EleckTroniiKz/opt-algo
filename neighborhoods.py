from abc import ABC, abstractmethod
import random
from itertools import permutations

class NeighborhoodStrategy(ABC):
    @abstractmethod
    def generate_neighbors(self, solution, problem_data):
        pass


class GeometryBasedStrategy(NeighborhoodStrategy):
    def generate_neighbors(self, solution, problem_data):
        neighbors = []
        for i in range(len(solution)):
            for j in range(len(solution)):
                if i != j:
                    for rect in solution[i]:
                        new_solution = [list(box) for box in solution]
                        new_solution[i].remove(rect)
                        new_solution[j].append(rect)
                        if not new_solution[i]:  # Remove empty box
                            del new_solution[i]
                        neighbors.append(new_solution)
        return neighbors

class RuleBasedStrategy(NeighborhoodStrategy):
    def generate_neighbors(self, solution, problem_data):
        rect_permutations = list(permutations(problem_data.rectangles))
        perm_index = random.randint(0, len(rect_permutations) - 1)
        current_perm = list(rect_permutations[perm_index])
        if len(current_perm) > 1:
            idx1, idx2 = random.sample(range(len(current_perm)), 2)
            current_perm[idx1], current_perm[idx2] = current_perm[idx2], current_perm[idx1]
            new_solution = [[rect] for rect in current_perm]
            return [new_solution]
        return [solution]
    
class OverlapStrategy(NeighborhoodStrategy):

    def __init__(self, initial_overlap):
        self.initial_overlap = initial_overlap
        self.current_overlap = initial_overlap

    def generate_neighbors(self, solution, problem_data):
        neighbors = []
        for i in range(len(solution)):
            for j in range(len(solution)):
                if i != j:
                    for index, rect in enumerate(solution[i]):
                        # Try moving rect to another box and check overlap
                        for target_rect in solution[j]:
                            if self.check_overlap_allowed(rect, target_rect, problem_data):
                                new_solution = [list(box) for box in solution]
                                new_solution[i].remove(rect)
                                new_solution[j].append(rect)
                                if not new_solution[i]:  # Remove empty box
                                    del new_solution[i]
                                neighbors.append(new_solution)
        return neighbors
    
    def update_threshold(self, decrement):
        self.current_overlap = max(0, self.current_overlap - decrement)

    def calculate_overlap(self, rectangle1, rectangle2):
        x1, y1, w1, h1 = rectangle1
        x2, y2, w2, h2 = rectangle2

        # Calculate the coordinates of the overlap rectangle
        overlap_x1 = max(x1, x2)
        overlap_y1 = max(y1, y2)
        overlap_x2 = min(x1 + w1, x2 + w2)
        overlap_y2 = min(y1 + h1, y2 + h2)

        # Calculate dimensions of the overlap area
        overlap_width = max(0, overlap_x2 - overlap_x1)
        overlap_height = max(0, overlap_y2 - overlap_y1)

        return overlap_width * overlap_height
    
    def check_overlap_allowed(self, rectangle1, rectangle2, problem_data):
        overlap_area = self.calculate_overlap(rectangle1, rectangle2)
        max_area = max(rectangle1[2] * rectangle1[3], rectangle2[2] * rectangle2[3])  # width * height
        overlap_ratio = overlap_area / max_area

        # Check if overlap is within the current allowed threshold
        return overlap_ratio <= self.current_overlap