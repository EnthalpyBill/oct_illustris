# Copyright (c) 2021 Bill Chen
# License: MIT (see LICENSE)

import os

class Runner(object):

    def __init__(self, base_path):
        super(Runner, self).__init__()
        self._base_path = os.path.abspath(base_path)
        
    def generate_runner(self):
        """
        Generate a test_runner function fot _base_path
        """

        def test_runner(args=[], plugins=[]):
            if not len(args) or not os.path.exists(args[-1]):
                args.insert(len(args), self._base_path)

            # Do not import pytest when not needed!
            try:
                import pytest
            except ImportError:
                msg = ("pytest is needed for test(). Install it with "
                    "`pip install pytest`")
                raise ImportError(msg)
            
            return pytest.main(args=args, plugins=plugins)

        return test_runner