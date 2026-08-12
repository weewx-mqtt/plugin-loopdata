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
                        # windrose.bands appears on its own whenever any windrose field is configured,
                        # holding the band edges in the target report’s windSpeed unit
                        # so a legend never hardcodes them. It is the one key you get without asking.
                        'fields': ['current.outTemp', 'day.outTemp.min.raw', 'day.outTemp.max.formatted',
                                   'current.barometer', 'current.barometer.raw', 'trend.barometer.raw', 'trend.barometer.desc',
                                   'year.rainRate', 'year.rainRate.raw', 'year.rain.sum', 'year.rain.sum.raw', 'year.rainRate.max', 'year.rainRate.max.raw',
                                    'current.windSpeed', 'current.windSpeed.raw', 'current.windDir.raw', 'current.windDir.ordinal_compass',
                                    '10m.windGust.max', '10m.wind.gustdir.raw', '10m.wind.gustdir.ordinal_compass',
                                    'week.windrose.banded', 'week.windrose.calm',
                                    'month.windrose.sum', 'month.windrose.time',
                                    'almanac.sunrise', 'almanac.moon_phase',
                                    'almanac(horizon=-6).sun(use_center=1).rise', 'almanac(horizon=-6).sun(use_center=1).set',
                                    # Currently mock is getting in the way of these
                                    # 'station.uptime.long_form()', 'station.os_uptime.long_form()', 'station.version', 'station.python_version', 'station.hardware', 'station.location', 'station.altitude', 'station.latitude',
                                   ],
                    },
                },
            },
        }

        SUT = user.mqttloopdata.MQTTLoopData(mock_logger, None, plugin_dict, None, None, configobj.ConfigObj(weewx_dict))
        pkt = {
            'dateTime': time.time(),
            'usUnits': 1,
            'interval': 2 / 60,
            'windSpeed': 5,
            'windDir': 180,
            'outTemp': 79.812,
            'barometer': 5,
            'rain': 3
        }
        loopdata_pkt = SUT.update_packet(pkt)

        expected_loopdata_pkt = {
            'current.windSpeed': '5 mph',
            'current.windDir.raw': 180,
            '10m.wind.gustdir.raw': 180.0,
            'year.rain.sum': '3.00 in',
            'week.windrose.calm': 0.0,
            'current.windDir.ordinal_compass': 'S',
            'day.outTemp.max.formatted': '79.8',
            'year.rain.sum.raw': 3.0,
            '10m.wind.gustdir.ordinal_compass': 'S',
            'current.barometer': '5.000 inHg',
            'current.windSpeed.raw': 5,
            'month.windrose.sum': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.002777777777777778, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'day.outTemp.min.raw': 79.812, 
            'week.windrose.banded': [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 2.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 
                                     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
            'current.outTemp': '79.8°F',
            'current.barometer.raw': 5,
            'month.windrose.time': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'windrose.bands': [1.1, 4.7, 8.1, 12.8, 19.7, 24.8],
            'almanac.moon_phase': 'New'}

        print(pkt)
        print('')
        print(loopdata_pkt)
        self.assertDictEqual(loopdata_pkt, expected_loopdata_pkt)
        print("done")

if __name__ == '__main__':
    helpers.run_tests()
