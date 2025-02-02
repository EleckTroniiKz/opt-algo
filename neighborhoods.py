import random
from abc import ABC, abstractmethod

from objects import Box, RecPac_Solution, Rectangle
from problem import RectanglePacker


class NeighborhoodStrategy(ABC):
    @abstractmethod
    def generate_neighbor(self, solution, temperature: float):
        pass


class GeometryBasedStrategy(NeighborhoodStrategy):
    def __init__(self, problem: RectanglePacker):
        self.x = 2
        self.problem = problem

    def generate_neighbor(self, solution: RecPac_Solution, temperature: float):
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

        move_intensity = max(1, int(len(box_from.rectangles) / self.x))

        for _ in range(move_intensity):
            rect_to_move = random.choice(box_from.rectangles)
            box_from.remove_rectangle(rect_to_move)

            counter = 0

            while True:
                if random.random() < 0.5:  # Move within the same box
                    rect_to_move.x = random.randint(0, box_from.box_length - rect_to_move.width)
                    rect_to_move.y = random.randint(0, box_from.box_length - rect_to_move.height)
                    if self.problem.does_rectangle_fit_into_position(box_from, rect_to_move):
                        box_from.add_rectangle(rect_to_move)
                        break

                else:  # Move to another box
                    box_to = random.choice(new_solution.boxes)
                    rect_to_move.x = random.randint(0, box_to.box_length - rect_to_move.width)
                    rect_to_move.y = random.randint(0, box_to.box_length - rect_to_move.height)
                    if self.problem.does_rectangle_fit_into_position(box_to, rect_to_move):
                        box_to.add_rectangle(rect_to_move)
                        break

                counter += 1

                if counter > 20:
                    break

        self.x += 1

        return new_solution


class RuleBasedStrategy(NeighborhoodStrategy):
    def generate_neighbor(self, solution: RecPac_Solution):
        if not solution.boxes:
            return solution

        new_solution = RecPac_Solution()
        new_solution.set_boxes([Box(box.box_length) for box in solution.boxes])

        rectangles = [rect for box in solution.boxes for rect in box.rectangles]
        random.shuffle(rectangles)

        for i, rect in enumerate(rectangles):
            box_idx = i % len(new_solution.boxes)
            new_solution.boxes[box_idx].add_rectangle(rect)

        return new_solution


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
