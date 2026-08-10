#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring
# pylint: disable=invalid-name

import unittest
import mock

import configobj
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
        mock_engine = mock.Mock()
        mock_engine.stn_info.altitude_vt = (0, 'meter')
        plugin_dict = {
            'enabled': True,
            'topics': {},
        }

        weewx_dict = {
            'engine': mock_engine,
            'config_dict': {
                'WEEWX_ROOT': '',
                'DataBindings': {
                    'wx_binding': {},
                },
                'Databases': {
                    'archive_sqlite': {
                        'database_type': 'SQLite',
                        'database_name': 'integration.sdb',
                    },
                },
                'DatabaseTypes': {
                    'SQLite': {
                        'driver': 'weedb.sqlite',
                        # Unfortunately, in memory DB will not work
                        # 'database_name': ':memory:',
                        'SQLITE_ROOT': 'bin/user/tests/integ/data',
                    },
                },
                'StdConvert': {},
                'StdReport': {
                    'SKIN_ROOT': '',
                    'data_binding': 'wx_binding',
                    'LoopDataReport': {},
                },
                'MQTTLoopData': {
                    'RsyncSpec': {
                        'enable': False,
                        'compress': False,
                        'log_success': False,
                    },
                },
            },
        }

        user.mqttloopdata.MQTTLoopData(mock_logger, None, plugin_dict, None, None, configobj.ConfigObj(weewx_dict))

if __name__ == '__main__':
    helpers.run_tests()
