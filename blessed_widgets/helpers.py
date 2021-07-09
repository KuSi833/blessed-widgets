from __future__ import annotations
import numpy as np
from typing import Any, List, Optional, TypeVar, cast, overload


def gaussian(x, mean, std):
    return np.exp(-np.power(x - mean, 2.) / (2 * np.power(std, 2.)))


X = TypeVar('X')


def getFirstAssigned(options: List[Optional[X]], default: X) -> X:
    for option in options:
        if option:
            return option
    return default
