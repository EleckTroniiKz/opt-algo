from abc import ABC, abstractmethod
from typing import List

from objects import Box, RecPac_Solution, Rectangle


class OptimizationProblem(ABC):

    @abstractmethod
    def basic_solution(self):
        pass

    @abstractmethod
    def add_to_solution(self, solution, instance) -> object:
        pass


class RectanglePacker(OptimizationProblem):

    def __init__(self, rectangles: List[Rectangle], box_length: int):
        self.rectangles = rectangles
        self.box_length = box_length

    def __repr__(self):
        return f"RectanglePacker(rectangles={self.rectangles}, box_length={self.box_length}"

    def add_to_solution(self, solution: RecPac_Solution, instance: Rectangle):
        # place the rectangle in one of the boxes. If it does not fit, it will add a new box, and initialize the rectangle at 0, 0

        if solution == None:
            return None

        for box in solution.boxes:
            x, y = self.fit_rectangle_inside_box(box, instance)
            if x is not None and y is not None:
                instance.x, instance.y = x, y
                box.add_rectangle(instance)
                return solution

            rectangle_rotated = instance
            rectangle_rotated.width, rectangle_rotated.height = instance.height, instance.width
            x, y = self.fit_rectangle_inside_box(box, rectangle_rotated)
            if x is not None and y is not None:
                rectangle_rotated.x, rectangle_rotated.y = x, y
                box.add_rectangle(instance)
                return solution

        # If no box can fit the rectangle, create a new box
        new_box = Box(self.box_length)
        instance.x, instance.y = 0, 0
        new_box.add_rectangle(instance)
        solution.add_box(new_box)
        return solution

    def fit_rectangle_inside_box(self, box: Box, rectangle: Rectangle):
        # check if rectangle fits into the box provided. 
        # if it does, it returns the x, y coordinates that it can be placed into the box. 
        # if it doesn't it returns None, None

        for y in range(self.box_length - rectangle.height + 1):  # Iterate within box height
            for x in range(self.box_length - rectangle.width + 1):  # Iterate within box width
                fits = True
                for rect in box.rectangles:
                    # Check for overlap with any existing rectangles
                    if (
                            x < rect.x + rect.width and x + rect.width > rect.x and
                            y < rect.y + rect.height and y + rect.height > rect.y
                    ):
                        fits = False
                        break

                if fits:
                    return x, y  # Return the valid position

        return None, None

    def does_rectangle_fit_into_position(self, box: Box, rectangle: Rectangle):

        for rect in box.rectangles:
            if (
                    rectangle.x < rect.x + rect.width and rectangle.x + rectangle.width > rect.x and
                    rectangle.y < rect.y + rect.height and rectangle.y + rectangle.height > rect.y
            ):
                return False

        return True

    def basic_solution(self):
        """Creates a solution, in which each rectangle has its own box

        Returns:
            RecPac_Solution: solution with one box per rectangle
        """
        solution = RecPac_Solution()
        for rectangle in self.rectangles:
            box = Box(self.box_length)
            rectangle.x, rectangle.y = 0, 0
            box.add_rectangle(rectangle)
            solution.add_box(box)
        return solution
