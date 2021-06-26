from __future__ import annotations
import numpy as np
from typing import Any, List, Optional, TypeVar, cast, overload


def gaussian(x, mean, std):
    return np.exp(-np.power(x - mean, 2.) / (2 * np.power(std, 2.)))


X = TypeVar('X')


def getAssigned(option: Optional[X], default: X) -> X:
    if option:
        return option
    return default


def returnA() -> str:
    return 'a'
