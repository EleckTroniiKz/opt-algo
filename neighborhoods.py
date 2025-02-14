import copy
import random
from abc import ABC, abstractmethod

from objects import Box, RecPac_Solution, Rectangle
from problem import RectanglePacker, OptimizationProblem


class NeighborhoodStrategy(ABC):
    @abstractmethod
    def generate_neighbor(self, solution):
        pass


class GeometryBasedStrategy(NeighborhoodStrategy):
    def __init__(self, problem: OptimizationProblem):
        self.problem = problem

    def generate_neighbor(self, solution: RecPac_Solution):
        if not solution.boxes:
            return solution

        new_solution = copy.deepcopy(solution)

        box_from = new_solution.boxes[-1]
        if not box_from.rectangles:
            return new_solution

        for _ in range(len(box_from.rectangles)):
            rect_to_move = random.choice(box_from.rectangles)
            box_from.remove_rectangle(rect_to_move)

            index = 0

            while True:
                box_to = new_solution.boxes[index]

                x, y, rotated = self.problem.fit_rectangle_inside_box(box_to, rect_to_move)

                if x is not None and y is not None:
                    rect_to_move.x = x
                    rect_to_move.y = y
                    if rotated:
                        rect_to_move.width, rect_to_move.height = rect_to_move.height, rect_to_move.width
                    box_to.add_rectangle(rect_to_move)
                    new_solution.check_if_box_empty(box_from)
                    break

                else:
                    index += 1

        return new_solution


class RuleBasedStrategy(NeighborhoodStrategy):
    def __init__(self, problem: OptimizationProblem, rule: str = "Absteigend nach Höhe"):
        self.problem = problem
        self.rule = rule

    def generate_neighbor(self, solution: RecPac_Solution):
        if not solution.boxes:
            return solution

        # Create a new empty solution
        current_solution = RecPac_Solution()

        # Extract all rectangles
        rectangles = [rect for box in solution.boxes for rect in box.rectangles]

        if len(rectangles) > 1:
            if self.rule == "Absteigend nach Höhe":
                rectangles = sorted(rectangles, key=lambda rect: rect.height, reverse=True)
            elif self.rule == "Absteigend nach Breite":
                rectangles = sorted(rectangles, key=lambda rect: rect.width, reverse=True)
            elif self.rule == "Absteigend nach Fläche":
                rectangles = sorted(rectangles, key=lambda rect: rect.height*rect.width, reverse=True)

            # Pick a small rectangle from the first half
            small_rectangles = rectangles[:len(rectangles) // 2]
            selected = random.choice(small_rectangles)

            # Swap with its neighbor
            i = rectangles.index(selected)
            j = i + 1 if i < len(rectangles) - 1 else i - 1
            rectangles[i], rectangles[j] = rectangles[j], rectangles[i]

        # Place rectangles **from scratch** to prevent overlaps
        for instance in rectangles:
            instance.x, instance.y = None, None  # Reset position before placing

            new_solution = self.problem.add_to_solution(current_solution, instance)

            if new_solution is not None:
                current_solution = new_solution

        return current_solution

class OverlapStrategy(NeighborhoodStrategy):

    def __init__(self, initial_overlap: float = 1.0, decay_rate: float = 0.05):
        self.overlap_percentage = initial_overlap
        self.decay_rate = decay_rate

    def generate_neighbor(self, solution: RecPac_Solution):
        if not solution.boxes:
            return solution

        new_solution = RecPac_Solution()
        new_solution.set_boxes([Box(box.box_length) for box in solution.boxes])

        for box in solution.boxes:
            for rect in box.rectangles:
                new_solution.boxes[solution.boxes.index(box)].add_rectangle(rect)

        box_from = random.choice(new_solution.boxes)
        if not box_from.rectangles:
            return new_solution

        rect_to_move = random.choice(box_from.rectangles)
        box_from.remove_rectangle(rect_to_move)

        box_to = random.choice(new_solution.boxes)
        rect_to_move.x = random.randint(0, box_to.box_length - rect_to_move.width)
        rect_to_move.y = random.randint(0, box_to.box_length - rect_to_move.height)

        if self.check_overlap(box_to, rect_to_move):
            box_to.add_rectangle(rect_to_move)
        else:
            box_from.add_rectangle(rect_to_move)  # Revert the move if too much overlap

        self.overlap_percentage = max(0, self.overlap_percentage - self.decay_rate)

        return new_solution

    def check_overlap(self, box: Box, rect: Rectangle):
        total_area = box.box_length ** 2
        overlapping_area = 0

        for existing_rect in box.rectangles:
            x_overlap = max(0, min(existing_rect.x + existing_rect.width, rect.x + rect.width) - max(existing_rect.x,
                                                                                                     rect.x))
            y_overlap = max(0, min(existing_rect.y + existing_rect.height, rect.y + rect.height) - max(existing_rect.y,
                                                                                                       rect.y))
            overlapping_area += x_overlap * y_overlap

        if overlapping_area / max(rect.width * rect.height, 1) <= self.overlap_percentage:
            return True
        return False
