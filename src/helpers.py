class Point():
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


def start_coordinates(p1: Point, p2: Point) -> tuple[int, int, int, int]:
    start_x = min(p1.x, p2.x)
    end_x = max(p1.x, p2.x)
    start_y = min(p1.y, p2.y)
    end_y = max(p1.y, p2.y)
    return start_x, end_x, start_y, end_y
