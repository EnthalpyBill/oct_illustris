# Copyright (c) 2021 Bill Chen
# License: MIT (https://opensource.org/licenses/MIT)

from . import core
from . import il_util
from . import loader
from . import octree

from .loader import load

__all__ = ["core", "il_util", "loader", "octree"]
__version__ = "0.0.dev"
__name__ = "oct_illustris"
__author__ = ["Bill Chen"]