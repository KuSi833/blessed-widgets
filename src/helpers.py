from constants import HAlignment, VAlignment


class Point():
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


def key_coordinates(p1: Point, p2: Point) -> tuple[int, int, int, int]:
    start_x = min(p1.x, p2.x)
    end_x = max(p1.x, p2.x)
    start_y = min(p1.y, p2.y)
    end_y = max(p1.y, p2.y)
    return start_x, end_x, start_y, end_y


def align_text_in_square(p1: Point, p2: Point, text: str,
                         padding: tuple[int, int, int, int],
                         h_align: HAlignment, v_align: VAlignment
                         ) -> tuple[int, int, str]:

    start_x, end_x, start_y, end_y = key_coordinates(p1, p2)
    width = end_x - start_x
    height = end_y - start_y

    max_text_len = width - (padding[1] + padding[3])
    text = text[:max_text_len]

    if h_align is HAlignment.LEFT:
        text_start_x = start_x + padding[3]
    elif h_align is HAlignment.MIDDLE:
        text_start_x = start_x + padding[3] + (width // 2) - (len(text) // 2)
    elif h_align is HAlignment.RIGHT:
        text_start_x = end_x - padding[1] - max_text_len

    if v_align is VAlignment.TOP:
        text_start_y = start_y + padding[0]
    elif v_align is VAlignment.MIDDLE:
        text_start_y = start_y + padding[0] + (height // 2)
    elif v_align is VAlignment.BOTTOM:
        text_start_y = end_y - padding[2]

    return text_start_x, text_start_y, text
