# Copyright (c) 2021 Bill Chen
# License: MIT (see LICENSE)

from . import core, il_util, loader, mesh
from .core import *
from .il_util import *
from .loader import *
from .mesh import *

__all__ = core.__all__ + il_util.__all__ + loader.__all__ + mesh.__all__
__version__ = "0.1.3"
__name__ = "mesh_illustris"
__author__ = ["Bill Chen"]

# Initialize test function
from .tests.run import Runner
test = Runner(__path__[0]).generate_runner()
__all__.append("test")

