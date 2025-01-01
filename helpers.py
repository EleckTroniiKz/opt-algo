import random
import copy

def generate_instances(n, min_width, max_width, min_height, max_height):
    """
    Generate rectangle Instances.
    n: amount of rectangles that will be generated
    min_width: A rectangle has to have a width that is bigger or equals min_width
    max_width: A rectangle has to have a width that is smaller or equals max_width
    min_height: A rectangle has to have a height that is bigger or equals min_height
    max_height: A rectangle has to have a height that is smaller or equals max_height
    """

    return [(random.randint(0, max_width - min_width), random.randint(0, max_height - min_height), random.randint(min_width, max_width), random.randint(min_height, max_height)) for _ in range(n)]

def rectangle_fits_in_box(box, rect, L):
    """
    Check if rectangle fits into the box. If not the result can be used, to initialize a new box.
    box: Position and Width/Height Data.
    rect: Width and Height of Rectangle
    L: Box dimensions
    """
    for x, y, w, h in box:
        if not (rect[0] + rect[2] <= x or x + w <= rect[0] or rect[1] + rect[3] <= y or y + h <= rect[1]):
            return False
    return rect[0] + rect[2] <= L and rect[1] + rect[3] <= L

def calculate_objective(boxes):
    """
    Objective function: Minimize the number of boxes.
    """
    return len(boxes)

def generate_neighbors(current_solution, L, neighborhood):
    """
    Generate neighbors by making small changes to the current solution.
    - Move a rectangle within the same box or between boxes.

    current_solution: The solution for which a neighbor will be generated
    L: Box dimensions
    """
    neighbors = []

    for i, box in enumerate(current_solution):
        for j, rect in enumerate(box):
            # Try moving the rectangle within the current box
            for dx in range(1, L):
                for dy in range(1, L):
                    new_solution = copy.deepcopy(current_solution)
                    new_solution[i].remove(rect)
                    x, y, w, h = rect
                    new_rect = (x + dx, y + dy, w, h)
                    if rectangle_fits_in_box(new_solution[i], new_rect, L):
                        new_solution[i].append(new_rect)
                        neighbors.append(new_solution)
            
            # Try moving the rectangle to a different box
            for k, other_box in enumerate(current_solution):
                if i != k:  # Don't move to the same box
                    new_solution = copy.deepcopy(current_solution)
                    new_solution[i].remove(rect)
                    if rectangle_fits_in_box(new_solution[k], rect, L):
                        new_solution[k].append(rect)
                        neighbors.append(new_solution)

    return neighbors