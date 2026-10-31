#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=wrong-import-order
# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring
# pylint: disable=invalid-name

import importlib.util
import pathlib
import queue
import unittest

import mock

import configobj

import user.mqttloopdata
import user.mqttcommon

# Due to importing user.loopdata, this project has a different 'user' directory (see .env).
# Therefore will dynamically load 'helpers'.
helpers_spec = importlib.util.spec_from_file_location("helpers", pathlib.Path(__file__).parent / '../helpers.py')
helpers = importlib.util.module_from_spec(helpers_spec)
helpers_spec.loader.exec_module(helpers)


def build_plugin(topics=None, loop_data=None, max_queue_size=100, loop_frequency=180):
    """ Build an MQTTLoopData holding only the state the methods under test use.

        The real __init__ drives the whole WeeWX loop-data machinery (database binder,
        renderers, accumulators); that path is integration tested in
        tests/integ/test_mqttloopdata.py. """
    SUT = user.mqttloopdata.MQTTLoopData.__new__(user.mqttloopdata.MQTTLoopData)  # pylint: disable=no-value-for-parameter
    SUT.enabled = True
    SUT.name = 'MQTTLoopData-test'
    SUT.monitor_config = {'monitor_queue': 'WARNING'}
    SUT.logger_queue = queue.Queue()
    SUT.max_queue_size = max_queue_size
    SUT.topics = {} if topics is None else topics
    SUT.loop_data = loop_data
    SUT.simple_cache = {}
    SUT.cfg = mock.Mock(loop_frequency=loop_frequency)
    SUT.update_packet = mock.Mock()
    return SUT


class TestInit(unittest.TestCase):
    def test_disabled_plugin_returns_before_setup(self):
        logger_queue = queue.Queue()
        SUT = user.mqttloopdata.MQTTLoopData(logger_queue, None, None, {'enable': False}, None, None, None)

        self.assertFalse(SUT.enabled)
        self.assertEqual(SUT.name, 'MQTTLoopData')
        self.assertEqual(logger_queue.get_nowait(),
                         user.mqttcommon.Logger.create_entry(
                             SUT.name, 'INFO', None, f"MQTTLoopData version: {user.mqttloopdata.VERSION}."))
        self.assertEqual(logger_queue.get_nowait(),
                         user.mqttcommon.Logger.create_entry(
                             SUT.name, 'INFO', None, "MQTTLoopData plugin not enabled, exiting"))
        self.assertTrue(logger_queue.empty())
        # The heavyweight setup is skipped entirely.
        self.assertFalse(hasattr(SUT, 'topics'))
        self.assertFalse(hasattr(SUT, 'loop_processor'))

    def test_missing_topics_raises_keyerror(self):
        with self.assertRaises(KeyError) as ctx:
            user.mqttloopdata.MQTTLoopData(queue.Queue(), None, None, {'enable': True}, None, None, None)
        self.assertEqual(ctx.exception.args, ('topics',))

    def test_missing_mqttloopdata_stanza_raises_keyerror(self):
        weewx_dict = {'config_dict': configobj.ConfigObj({})}
        plugin_dict = {'enable': True, 'topics': {}}
        with self.assertRaises(KeyError) as ctx:
            user.mqttloopdata.MQTTLoopData(queue.Queue(), None, None, plugin_dict, None, None, weewx_dict)
        self.assertEqual(ctx.exception.args, ('MQTTLoopData',))

    def test_topic_without_report_raises_keyerror(self):
        # A [[topics]] stanza without 'report' cannot map its record to loop data.
        weewx_dict = {'config_dict': configobj.ConfigObj({
            'MQTTLoopData': {},
            'StdReport': {'LoopDataReport': {}},
        })}
        plugin_dict = {'enable': True, 'topics': {'some/topic': {'enable': True}}}
        with self.assertRaises(KeyError) as ctx:
            user.mqttloopdata.MQTTLoopData(queue.Queue(), None, None, plugin_dict, None, None, weewx_dict)
        self.assertEqual(ctx.exception.args, ('report',))


class TestGetCallbacks(unittest.TestCase):
    def test_enabled_plugin_registers_both_callbacks(self):
        SUT = build_plugin()

        callbacks = SUT.get_callbacks()

        self.assertEqual(len(callbacks), 1)
        entry = callbacks[0]
        self.assertEqual(set(entry), {'on_weewx_data', 'update_record'})
        for name in ('on_weewx_data', 'update_record'):
            self.assertEqual(entry[name]['timing'], 'immediate')
            self.assertIs(entry[name]['callback'].__self__, SUT)
            self.assertIs(entry[name]['callback'].__func__, getattr(user.mqttloopdata.MQTTLoopData, name))

    def test_disabled_plugin_has_no_callbacks(self):
        SUT = user.mqttloopdata.MQTTLoopData(queue.Queue(), None, None, {'enable': False}, None, None, None)
        self.assertEqual(SUT.get_callbacks(), [])


class TestOnWeewxData(unittest.TestCase):
    def test_queue_size_below_max_resets_loop_data(self):
        SUT = build_plugin(max_queue_size=10)
        SUT.loop_data = {'LoopDataReport': {'outTemp': 70.1}}

        SUT.on_weewx_data({'queue_size': 3})

        self.assertIsNone(SUT.loop_data)
        self.assertTrue(SUT.logger_queue.empty())

    def test_queue_size_equal_to_max_resets_loop_data(self):
        # The check is <=, so a full queue still gets a new packet.
        SUT = build_plugin(max_queue_size=10)
        SUT.loop_data = {'LoopDataReport': {'outTemp': 70.1}}

        SUT.on_weewx_data({'queue_size': 10})

        self.assertIsNone(SUT.loop_data)
        self.assertTrue(SUT.logger_queue.empty())

    def test_queue_size_over_max_logs_monitor_and_keeps_loop_data(self):
        SUT = build_plugin(max_queue_size=10)
        loop_data = {'LoopDataReport': {'outTemp': 70.1}}
        SUT.loop_data = loop_data

        SUT.on_weewx_data({'queue_size': 11})

        # The packet is being dropped, so the current loop data stays around.
        self.assertIs(SUT.loop_data, loop_data)
        msg = SUT.logger_queue.get_nowait()
        self.assertEqual(msg['name'], 'MQTTLoopData-test')
        self.assertEqual(msg['log_type'], 'WARNING')  # monitor_config['monitor_queue']
        self.assertTrue(msg['msg_text'].startswith('monitor:'))
        self.assertIn('11', msg['msg_text'])
        self.assertIn('10', msg['msg_text'])
        self.assertTrue(SUT.logger_queue.empty())


class TestUpdateRecord(unittest.TestCase):
    def test_unknown_topic_is_ignored(self):
        SUT = build_plugin(topics={'known/topic': {'report': 'LoopDataReport'}})
        data = {'dateTime': 1000}

        SUT.update_record(None, 'unknown/topic', data, None, None, None)

        self.assertEqual(data, {'dateTime': 1000})
        SUT.update_packet.assert_not_called()
        self.assertTrue(SUT.logger_queue.empty())

    def test_first_topic_builds_and_merges_loop_data(self):
        SUT = build_plugin(topics={'a/topic': {'report': 'LoopDataReport'}}, loop_frequency=180)
        SUT.update_packet.return_value = {'LoopDataReport': {'barometer': 1010.2}}
        data = {'dateTime': 1000, 'usUnits': 1}

        SUT.update_record(None, 'a/topic', data, None, None, None)

        # The record was copied before it was extended, so data itself only
        # gains the merged report fields - not the loop interval.
        SUT.update_packet.assert_called_once()
        self.assertIs(SUT.update_packet.call_args[0][0], SUT.simple_cache)
        self.assertEqual(SUT.simple_cache['interval'], 180 / 60.0)
        self.assertEqual(SUT.simple_cache['dateTime'], 1000)
        self.assertNotIn('interval', data)
        self.assertEqual(data, {'dateTime': 1000, 'usUnits': 1, 'barometer': 1010.2})
        # The generated loop data is cached for the other topics of this packet.
        self.assertEqual(SUT.loop_data, {'LoopDataReport': {'barometer': 1010.2}})

    def test_second_topic_of_same_packet_reuses_loop_data(self):
        topics = {'a/topic': {'report': 'ReportA'}, 'b/topic': {'report': 'ReportB'}}
        SUT = build_plugin(topics=topics)
        SUT.update_packet.return_value = {'ReportA': {'outTemp': 70.0}, 'ReportB': {'barometer': 1010.2}}
        data_a = {'dateTime': 1000}
        data_b = {'dateTime': 1000}

        SUT.update_record(None, 'a/topic', data_a, None, None, None)
        SUT.update_record(None, 'b/topic', data_b, None, None, None)

        self.assertEqual(SUT.update_packet.call_count, 1)
        self.assertEqual(data_a, {'dateTime': 1000, 'outTemp': 70.0})
        self.assertEqual(data_b, {'dateTime': 1000, 'barometer': 1010.2})
        self.assertTrue(SUT.logger_queue.empty())

    def test_missing_report_in_loop_data_logs_error_and_leaves_data_alone(self):
        SUT = build_plugin(topics={'a/topic': {'report': 'NoSuchReport'}})
        SUT.update_packet.return_value = {'LoopDataReport': {'barometer': 1010.2}}
        data = {'dateTime': 1000}

        SUT.update_record(None, 'a/topic', data, None, None, None)

        self.assertEqual(data, {'dateTime': 1000})
        msg = SUT.logger_queue.get_nowait()
        self.assertEqual(msg['log_type'], 'ERROR')
        self.assertIn('NoSuchReport', msg['msg_text'])
        self.assertIn('in loop data', msg['msg_text'])
        self.assertTrue(SUT.logger_queue.empty())

    def test_queue_reset_triggers_regeneration_for_next_packet(self):
        SUT = build_plugin(topics={'a/topic': {'report': 'LoopDataReport'}})
        SUT.update_packet.return_value = {'LoopDataReport': {'barometer': 1010.2}}
        data_1 = {'dateTime': 1000}
        data_2 = {'dateTime': 2000}

        SUT.update_record(None, 'a/topic', data_1, None, None, None)
        SUT.on_weewx_data({'queue_size': 0})
        SUT.update_record(None, 'a/topic', data_2, None, None, None)

        # on_weewx_data reset loop_data, so the new packet regenerates it; the
        # simple cache is never cleared and carries the latest values forward.
        self.assertEqual(SUT.update_packet.call_count, 2)
        second_cache = SUT.update_packet.call_args_list[1][0][0]
        self.assertIs(second_cache, SUT.simple_cache)
        self.assertEqual(second_cache['dateTime'], 2000)
        self.assertEqual(data_2, {'dateTime': 2000, 'barometer': 1010.2})


class TestSimpleMethods(unittest.TestCase):
    def test_loginfo_queues_info_message(self):
        SUT = build_plugin()

        SUT.loginfo('hello')

        self.assertEqual(SUT.logger_queue.get_nowait(),
                         user.mqttcommon.Logger.create_entry('MQTTLoopData-test', 'INFO', None, 'hello'))
        self.assertTrue(SUT.logger_queue.empty())

    def test_pre_loop_and_new_loop_are_noops(self):
        SUT = build_plugin()
        self.assertIsNone(SUT.pre_loop(None))
        self.assertIsNone(SUT.new_loop(None))


if __name__ == '__main__':
    helpers.run_tests()
