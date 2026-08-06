#
#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.

import copy
import time

from typing import Dict

import weewx
import weeutil

from user.loopdata import Accumulators, ContinuousAccum, LoopData, LoopProcessor  # pylint: disable=import-error,no-name-in-module

VERSION = "0.1.0-rc01"

class log:  # pylint: disable=invalid-name
    """ For compatability and maintability withh weewx-loopdata. """
    info = None

class MQTTLoopData(LoopData):
    """ Create loop data for MQTTPublish. """
    # def __init__(self, engine, config_dict):
    def __init__(self, logger, _name, plugin_dict, _mqtt_dict, _topics, weewx_dict):

        # ToDo: Currently only support publishing json - need to add a check
        self.enabled = plugin_dict.get('enabled', True)
        self.logger = logger
        if not self.enabled:
            self.logger("Not enabled, exiting")
            return

        self.topics = plugin_dict['topics']
        log.info = logger.loginf
        self.simple_cache = {}

        config_dict = weeutil.config.deep_copy(weewx_dict['config_dict'])
        config_dict['LoopData'] = {}
        config_dict['LoopData'] = weeutil.config.deep_copy(config_dict['MQTTLoopData'])

        super().__init__(weewx_dict['engine'], config_dict)

        # A separare thread is no longer needed to do the 'real' work.
        self.loop_processor = LoopProcessor(self.cfg)
        self.loop_processor.accumulators = self.setup_accumulators()

    def pre_loop(self, _event):
        """ Data is no longer 'retrieved' from WeeWX pipeline. """
        return

    def new_loop(self, _event):
        """ Data is no longer 'retrieved' from WeeWX pipeline. """
        return

    def setup_accumulators(self):
        """ This code is 'lifted' from new_loop. """
        # pylint: disable=protected-access
        binder = weewx.manager.DBBinder(self.config_dict)
        binding = self.config_dict.get('StdReport')['data_binding']
        dbm = binder.get_manager(binding)
        # ToDo: investigate what pkt_time is used for on initialization
        # pkt_time = to_int(event.packet['dateTime'])
        pkt_time = int(time.time())

        # Init day accumulator from day_summary
        day_summary = dbm._get_day_summary(time.time())
        # Init an accumulator
        timespan = weeutil.weeutil.archiveDaySpan(pkt_time)
        unit_system = day_summary.unit_system
        if unit_system is not None:
            # Database has a unit_system already (true unless the db just got intialized.)
            self.cfg.unit_system = unit_system
        day_accum = weewx.accum.Accum(timespan, unit_system=self.cfg.unit_system)
        for k in day_summary:
            day_accum.set_stats(k, day_summary[k].getStatsTuple())

        # Create fixed accums
        alltime_accum, self.cfg.obstypes.alltime = LoopData.create_alltime_accum(
            self.cfg.unit_system, self.cfg.archive_interval, self.cfg.obstypes.alltime, day_accum, dbm)
        rainyear_accum, self.cfg.obstypes.rainyear = LoopData.create_rainyear_accum(
            self.cfg.unit_system, self.cfg.archive_interval, self.cfg.obstypes.rainyear, pkt_time, self.cfg.rainyear_start, day_accum, dbm)
        year_accum, self.cfg.obstypes.year = LoopData.create_year_accum(
            self.cfg.unit_system, self.cfg.archive_interval, self.cfg.obstypes.year, pkt_time, day_accum, dbm)
        month_accum, self.cfg.obstypes.month = LoopData.create_month_accum(
            self.cfg.unit_system, self.cfg.archive_interval, self.cfg.obstypes.month, pkt_time, day_accum, dbm)
        week_accum, self.cfg.obstypes.week = LoopData.create_week_accum(
            self.cfg.unit_system, self.cfg.archive_interval, self.cfg.obstypes.week, pkt_time, self.cfg.week_start, day_accum, dbm)
        hour_accum, self.cfg.obstypes.hour = LoopData.create_hour_accum(
            self.cfg.unit_system, self.cfg.archive_interval, self.cfg.obstypes.hour, pkt_time, day_accum, dbm,
            archive_delay=self.cfg.archive_delay)

        # Create continuous accums
        continuous_accums: Dict[str, ContinuousAccum] = {}
        for per, obstypes in self.cfg.obstypes.continuous.items():
            if per == 'trend':
                timelength = self.cfg.time_delta
            elif LoopData.is_hour_period(per):
                timelength = int(per[:-1])*3600
            elif LoopData.is_minute_period(per):
                timelength = int(per[:-1])*60

            cont_accum, obstypes = LoopData.create_continuous_accum(
                per, self.cfg.unit_system, self.cfg.archive_interval, obstypes, timelength, day_accum, dbm,
                archive_delay=self.cfg.archive_delay)
            if cont_accum:
                continuous_accums[per], self.cfg.obstypes.continuous[per]  = cont_accum, obstypes

        # Create windrose accums (span periods seeded by one SQL GROUP BY
        # each, continuous periods by archive replay).
        windrose_span_accums, windrose_continuous_accums = \
            LoopData.create_windrose_accums(self.cfg, dbm, pkt_time)

        return(Accumulators(
            alltime_accum       = alltime_accum,
            rainyear_accum      = rainyear_accum,
            year_accum          = year_accum,
            month_accum         = month_accum,
            week_accum          = week_accum,
            day_accum           = day_accum,
            hour_accum          = hour_accum,
            continuous          = continuous_accums,
            windrose_span       = windrose_span_accums,
            windrose_continuous = windrose_continuous_accums))

    def update_packet(self, pkt):
        """ This code is 'lifted from 'process_queue. """
        # pylint: disable=unnecessary-pass, not-callable
        try:
            windrun_val = weewx.wxxtypes.WXXTypes.calc_windrun('windrun', pkt)
            pkt['windrun'] = windrun_val[0]
        except weewx.CannotCalculate:
            log.info('Cannot calculate windrun.')
            pass

        try:
            beaufort_val = weewx.wxxtypes.WXXTypes.calc_beaufort('beaufort', pkt)
            pkt['beaufort'] = beaufort_val[0]
        except weewx.CannotCalculate:
            log.info('Cannot calculate beaufort.')
            pass

        # Process new packet.
        return LoopProcessor.generate_loopdata_dictionary(
            pkt, self.loop_processor.cfg, self.loop_processor.accumulators, self.loop_processor.almanac_eval,
            self.loop_processor.station_eval)

    def get_callbacks(self):
        """ The callbacks. """
        if not self.enabled:
            return []

        return [
            {
                'update_record': {
                    'timing': 'immediate',
                    'callback': self.update_record
                },
            },
        ]

    def update_record(self, _mqtt_client, topic, data, _units, _qos, _retain):
        """ Run code when MQTT record is updated. """
        if topic in self.topics:
            pkt = copy.deepcopy(data)
            pkt['interval']     = self.cfg.loop_frequency / 60.0
            self.simple_cache.update(pkt)

            loopdata_pkt = self.update_packet(self.simple_cache)
            data.update(loopdata_pkt)
