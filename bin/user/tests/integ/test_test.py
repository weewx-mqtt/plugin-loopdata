#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring
# pylint: disable=invalid-name

import unittest
import mock

import importlib
import pathlib

import user.mqttloopdata

# Due to importing user.loopdata, this project has a different 'user' directory (see .env).
# Therefore will dynamically load 'user.helpers'.
helpers_spec = importlib.util.spec_from_file_location("helpers", pathlib.Path(__file__).parent / '../helpers.py')
helpers = importlib.util.module_from_spec(helpers_spec)
helpers_spec.loader.exec_module(helpers)

class TestUnitSimpleClass(unittest.TestCase):
    def test_test(self):
        mock_logger = mock.Mock()
        config_dict = {
            'enabled': False,
        }

        user.mqttloopdata.MQTTLoopData(mock_logger, None, config_dict, None, None, None)

if __name__ == '__main__':

    helpers.run_tests()
 