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
import time

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
                    'Include': {
                        'fields': ['current.outTemp', 'day.outTemp.min.raw', 'day.outTemp.max.formatted'],
                    },
                    # fields = current.outHumidity, current.outHumidity.raw, day.outHumidity.min.raw, day.outHumidity.max.raw, 
                    # current.windSpeed, current.windSpeed.raw, current.windDir.raw, current.windDir.ordinal_compass, 
                    # 10m.windGust.max, 10m.wind.gustdir.raw, 10m.wind.gustdir.ordinal_compass, 
                    # current.barometer, current.barometer.raw, trend.barometer.raw, trend.barometer.desc, 
                    # current.rainRate, current.rainRate.raw, day.rain.sum, day.rain.sum.raw, day.rainRate.max, day.rainRate.max.raw, 
                    # current.dewpoint, current.dewpoint.raw, day.dewpoint.min.raw, day.dewpoint.max.raw, day.dewpoint.min.formatted, day.dewpoint.max.formatted, 
                    # current.appTemp, current.appTemp.raw, day.appTemp.min.raw, day.appTemp.max.raw, day.appTemp.min.formatted, day.appTemp.max.formatted, 
                    # current.UV, current.UV.raw, day.UV.max, 
                    # current.radiation, current.radiation.raw, day.radiation.max, 
                    # current.pm2_5, current.pm2_5_aqi.raw, current.pm2_5_aqi.formatted, 
                    # day.windrose.banded, day.windrose.calm, 
                    # unit.label.outTemp, unit.label.barometer, unit.label.rain, unit.label.rainRate, unit.label.windSpeed
                },
            },
        }

        SUT = user.mqttloopdata.MQTTLoopData(mock_logger, None, plugin_dict, None, None, configobj.ConfigObj(weewx_dict))
        pkt = {
            'dateTime': time.time(),
            'usUnits': 1,
            'interval': 2 / 60,
            'windSpeed': 5,
            'outTemp': 79.812,
        }
        loopdata_pkt = SUT.update_packet(pkt)

        print(pkt)
        print(loopdata_pkt)
        print("done")

if __name__ == '__main__':
    helpers.run_tests()
