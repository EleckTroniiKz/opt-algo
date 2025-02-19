import random
from rtree import index
import copy
import itertools

from classes.base_classes import  OptimizationProblem, Solution, Neighborhood
from classes.rectangle_packer_types import RecPac_Solution, Rectangle, Box
import classes.helpers

from .enums import Rules

class GeometryBasedStrategy(Neighborhood):
    def __init__(self, problem: OptimizationProblem, solution_type: type):
        self.problem = problem
        self.solution_type = solution_type

    def generate_neighbor(self, solution: Solution):
        if not solution.boxes:
            return solution

        new_solution = copy.deepcopy(solution)

        box_from = new_solution.boxes[-1]
        if not box_from.items:
            return new_solution

        for _ in range(len(box_from.items)):
            rect_to_move = random.choice(box_from.items)
            box_from.remove_rectangle(rect_to_move)

            index = 0

            while True:
                box_to = new_solution.boxes[index]

                x, y, rotated = self.problem.find_valid_assignment(box_to, rect_to_move)

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


class RuleBasedStrategy(Neighborhood):
    def __init__(self, problem: OptimizationProblem, rule: str = Rules.HEIGHT_FIRST):
        self.problem = problem
        self.rule = rule

    def generate_neighbor(self, solution: Solution):
        if not solution.boxes:
            return solution

        current_solution = RecPac_Solution()
        items = [item for box in solution.boxes for item in box.items]

        if len(items) > 1:
            items = classes.helpers.apply_rule(items, self.rule)

            small_rectangles = items[:len(items) // 2]
            selected = random.choice(small_rectangles)

            i = items.index(selected)
            j = i + 1 if i < len(items) - 1 else i - 1
            items[i], items[j] = items[j], items[i]

        for item in items:
            item.x, item.y = None, None

            new_solution = self.problem.add_to_solution(current_solution, item)

            if new_solution is not None:
                current_solution = new_solution

        return current_solution

class OverlapStrategy(Neighborhood):
    def __init__(self, problem: OptimizationProblem, initial_overlap: float = 1.0, decay_rate: float = 0.05):
        self.overlap_percentage = initial_overlap
        self.decay_rate = decay_rate
        self.problem = problem

    def generate_neighbor(self, solution: Solution):
        new_solution = copy.deepcopy(solution)

        for box in new_solution.boxes:
            # Aktualisiere den räumlichen Index für das aktuelle Box
            spatial_index = self.build_spatial_index(box)

            items_to_relocate = [item for item in box.items if not self.check_overlap(box, spatial_index, item)]
            for item in items_to_relocate:
                box.remove_rectangle(item)

            for item in items_to_relocate:
                placed = False
                for target_box in itertools.chain([box], new_solution.boxes):
                    if placed:
                        break
                    x, y, rotated = self.problem.find_valid_assignment(target_box, item, self.overlap_percentage * 0.3)
                    if x is not None:
                        item.x, item.y = x, y
                        if rotated:
                            item.width, item.height = item.height, item.width
                        target_box.add_rectangle(item)
                        placed = True

                if not placed:
                    new_box = Box(new_solution.boxes[0].box_length)
                    item.x, item.y = 0, 0
                    new_box.add_rectangle(item)
                    new_solution.add_box(new_box)

        self.overlap_percentage = max(0.0, round(self.overlap_percentage - self.decay_rate, 6))
        return new_solution

    def build_spatial_index(self, box: Box):
        # Erstelle einen räumlichen Index und füge alle Rechtecke hinzu
        idx = index.Index()
        for i, rect in enumerate(box.items):
            idx.insert(i, (rect.x, rect.y, rect.x + rect.width, rect.y + rect.height))
        return idx

    def check_overlap(self, box: Box, spatial_index, rect: Rectangle):
        rect_bounds = (rect.x, rect.y, rect.x + rect.width, rect.y + rect.height)
        max_rect_area = rect.width * rect.height

        # Finde potenzielle Überschneidungen
        potential_overlaps = list(spatial_index.intersection(rect_bounds))

        for i in potential_overlaps:
            existing_rect = box.items[i]  # Jetzt ist 'box' korrekt übergeben und zugreifbar
            if existing_rect is rect:
                continue

            x_overlap = max(0, min(existing_rect.x + existing_rect.width, rect.x + rect.width) - max(existing_rect.x, rect.x))
            y_overlap = max(0, min(existing_rect.y + existing_rect.height, rect.y + rect.height) - max(existing_rect.y, rect.y))

            overlap_area = x_overlap * y_overlap
            if self.overlap_percentage == 0.0 and overlap_area > 0:
                return False

            denominator = min(max_rect_area, existing_rect.width * existing_rect.height)
            if overlap_area / denominator > self.overlap_percentage:
                return False

        return True
