import time

import weewx
import weeutil

from user.loopdata import Accumulators, ContinuousAccum, LoopData, LoopProcessor

from typing import Dict

class MQTTLoopData(LoopData):
    # def __init__(self, engine, config_dict):
    def __init__(self, logger, name, plugin_dict, _mqtt_dict, _topics, weewx_dict):
        super().__init__(weewx_dict['engine'], weewx_dict['config_dict'])

        loop_processor = LoopProcessor(self.cfg)
        loop_processor.accumulators = self.setup_accumulators()

    def pre_loop(self, event):
        return

    def new_loop(self, event):
        return

    def setup_accumulators(self):
        binder = weewx.manager.DBBinder(self.config_dict)
        binding = self.config_dict.get('StdReport')['data_binding']
        dbm = binder.get_manager(binding)
        # pkt_time = to_int(event.packet['dateTime'])
        pkt_time = time.time()

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

    def get_callbacks(self):
        """ The callbacks. """

        return []
