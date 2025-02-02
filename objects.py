from typing import List


class Rectangle:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        return f"Rectangle(x={self.x}, y={self.y}, width={self.width}, height={self.height})"


class Box:
    def __init__(self, box_length: int):
        self.box_length = box_length
        self.rectangles: Rectangle = []
        self.last_covered_area = None

    def __repr__(self):
        return f"Box(box_length={self.box_length}, rectangles={self.rectangles}, last_covered_area={self.last_covered_area})"

    def add_rectangle(self, rectangle: Rectangle):
        self.rectangles.append(rectangle)

    def remove_rectangle(self, rectangle: Rectangle):
        self.rectangles.remove(rectangle)

    def calculate_covered_area(self):
        total_box_area = self.box_length ** 2
        covered_by_rectangles = 0

        for rectangle in self.rectangles:
            covered_by_rectangles += rectangle.width * rectangle.height

        return (covered_by_rectangles / total_box_area) * 100


class RecPac_Solution:
    def __init__(self):
        self.boxes: List[Box] = []

    def add_box(self, box: Box):
        self.boxes.append(box)

    def set_boxes(self, boxes: List[Box]):
        self.boxes = boxes

    def evaluate_solution(self):
        """Calculates the total area, that is covered by all rectangles, over all boxes

        Args:
            solution (RecPac_Solution): the solution that will be evaluated

        Returns:
            number: total_covered_area in percent (%)
        """
        rectangle_areas = 0
        if len(self.boxes) == 0:
            return 0
        box_length = self.boxes[0].box_length
        box_amounts = len(self.boxes)
        for box in self.boxes:
            coverage = box.calculate_covered_area()
            rectangle_areas += (coverage / (box_length ** 2)) / 100

        total_covered_area = (rectangle_areas / (box_length ** 2) * box_amounts) * 100
        return total_covered_area

    def __repr__(self):
        return f"RecPac_Solution(boxes={self.boxes})"
