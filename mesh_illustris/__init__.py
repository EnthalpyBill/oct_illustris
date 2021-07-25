# Copyright (c) 2021 Bill Chen
# License: MIT (https://opensource.org/licenses/MIT)

from . import core, il_util, loader, mesh

__all__ = core.__all__ + il_util.__all__ + loader.__all__ + mesh.__all__

from .core import *
from .il_util import *
from .loader import *
from .mesh import *

__version__ = "0.0.dev"
__name__ = "mesh_illustris"
__author__ = ["Bill Chen"]