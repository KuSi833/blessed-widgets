from __future__ import annotations

# def align_text_in_square(square: Square, text: str,
#                          padding: List[int],
#                          h_align: HAlignment, v_align: VAlignment
#                          ) -> tuple[int, int, str]:

#     max_text_len = square.get_width() - (padding[1] + padding[3])
#     text = text[:max_text_len]

#     if h_align is HAlignment.LEFT:
#         text_start_x = square.get_edge(Sides.LEFT) + padding[3]
#     elif h_align is HAlignment.MIDDLE:
#         text_start_x = square.get_edge(Sides.LEFT) + padding[3] + (square.get_width() // 2) - (len(text) // 2)
#     elif h_align is HAlignment.RIGHT:
#         text_start_x = square.get_edge(Sides.RIGHT) - padding[1] - max_text_len

#     if v_align is VAlignment.TOP:
#         text_start_y = square.get_edge(Sides.TOP) + padding[0]
#     elif v_align is VAlignment.MIDDLE:
#         text_start_y = square.get_edge(Sides.TOP) - padding[0] - (square.get_height() // 2)
#     elif v_align is VAlignment.BOTTOM:
#         text_start_y = square.get_edge(Sides.BOTTOM) + padding[2]

#     return text_start_x, text_start_y, text

# # Typing
# from constants import HAlignment, VAlignment, Sides
# from typing import List
# from widgets import Square
