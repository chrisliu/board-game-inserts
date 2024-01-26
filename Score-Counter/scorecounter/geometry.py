import math
from typing import Tuple


def _compute_closest_point_on_circle(
    x_pt: int | float,
    y_pt: int | float,
    r: int | float,
    theta: int | float
) -> Tuple[int | float, int | float]:
    # Line formula: y = Mx + C
    M = math.tan(theta)
    C = y_pt - M * x_pt

    # After plugging in y into the circle formula, we get the following
    # terms for the quadratic formula.
    a = M ** 2 + 1
    b = 2 * M * C
    c = C ** 2 - r ** 2

    # Solve for possible points.
    x1 = (-b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
    y1 = M * x1 + C
    x2 = (-b - math.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
    y2 = M * x2 + C

    d1_sq = (x1 - x_pt) ** 2 + (y1 - y_pt) ** 2
    d2_sq = (x2 - x_pt) ** 2 + (y2 - y_pt) ** 2

    if d1_sq < d2_sq:
        return x1, y1
    return x2, y2
