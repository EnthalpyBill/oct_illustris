# Copyright (c) 2021 Bill Chen
# License: MIT (see LICENSE)

"""
run module provides a testing API.
"""

import os

class Runner(object):
    """Runner class provides a testing API."""

    def __init__(self, base_path):
        """
        Args:
            base_path (str): Base path to perform tests. 
        """

        super(Runner, self).__init__()
        self._base_path = os.path.abspath(base_path)
        
    def generate_runner(self):
        """
        Generate the _test_runner function fot self._base_path

        Returns:
            func: A function that calls pytest.main
        """

        def _test_runner(args=[], plugins=[]):
            if not len(args) or not os.path.exists(args[-1]):
                args.insert(len(args), self._base_path)

            # Do not import pytest when it's not needed!
            try:
                import pytest
            except ImportError:
                msg = ("pytest is needed for test(). Install it with "
                    "`pip install pytest`")
                raise ImportError(msg)
            
            return pytest.main(args=args, plugins=plugins)

        return _test_runner