#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring
# pylint: disable=invalid-name

import unittest
import mock

import user.tests.helpers

import user.mqttloopdata

class TestUnitSimpleClass(unittest.TestCase):
    def test_test(self):
        mock_logger = mock.Mock()
        config_dict = {
            'enabled': False,
        }

        SUT = user.mqttloopdata.MQTTLoopData(mock_logger, None, config_dict, None, None, None)

if __name__ == '__main__':
    user.tests.helpers.run_tests()
