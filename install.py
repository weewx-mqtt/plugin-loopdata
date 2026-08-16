#    Copyright (c) 2026 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

""" Installer for mqttloopdata plugin.

To uninstall run
wee_extension --uninstall=mqttloopdata
"""

from io import StringIO

import configobj

from weecfg.extension import ExtensionInstaller

VERSION = "0.1.0-rc01"

MQTTLOOPDATA_CONFIG = """

[MQTTLoopData]
    # -------------------------------------------------------------------------------------------------------
    # Augment MQTT data being published with 'loopdata', https://github.com/chaunceygardiner/weewx-loopdata
    #
    # **** Remember to MQTTLoopData to the plugins setting of MQTTPublish ****
    # -------------------------------------------------------------------------------------------------------

    # Whether the plugin is enabled or not.
    # Valid values: true or false
    # Default is true.
    enable = false

    # The plugin to be used.
    plugin = user.mqttloopdata.MQTTLoopData

    [[topics]]
        # The name of the topic to add the 'loopdata' to.
        [[[REPLACE_ME]]]

    #
    # The following are used by the weewx-loopdata extension, https://github.com/chaunceygardiner/weewx-loopdata
    #
    [[Formatting]]
        # The WeeWX report to target.
        # LoopData uses this report to determine the units to use and the formatting to apply.
        # If loop_data_dir is a relative path, it is relative to the directory of target_report.
        # Default is LoopDataReport.
        target_report = LoopDataReport

    [[LoopFrequency]]
        # The frequency of loop packets emitted by your device.
        # This is needed to give the proper weight to accumulator entries.
        # Default is 2.0.
        seconds = 2.0

    [[Include]]
        # The fields to include in the json file — a bare comma-separated list.
        # Each entry is a report tag with the $ removed; each becomes a key in loop-data.txt.
        # The complete grammar is here, https://chaunceygardiner.github.io/weewx-loopdata/field-reference.html
        # Default value is an empty list.
        fields = current.dateTime.raw, current.outTemp, current.outTemp.raw, day.outTemp.min.raw, day.outTemp.max.raw, day.outTemp.min.formatted, day.outTemp.max.formatted, current.outHumidity, current.outHumidity.raw, day.outHumidity.min.raw, day.outHumidity.max.raw, current.windSpeed, current.windSpeed.raw, current.windDir.raw, current.windDir.ordinal_compass, 10m.windGust.max, 10m.wind.gustdir.raw, 10m.wind.gustdir.ordinal_compass, current.barometer, current.barometer.raw, trend.barometer.raw, trend.barometer.desc, current.rainRate, current.rainRate.raw, day.rain.sum, day.rain.sum.raw, day.rainRate.max, day.rainRate.max.raw, current.dewpoint, current.dewpoint.raw, day.dewpoint.min.raw, day.dewpoint.max.raw, day.dewpoint.min.formatted, day.dewpoint.max.formatted, current.appTemp, current.appTemp.raw, day.appTemp.min.raw, day.appTemp.max.raw, day.appTemp.min.formatted, day.appTemp.max.formatted, current.UV, current.UV.raw, day.UV.max, current.radiation, current.radiation.raw, day.radiation.max, current.pm2_5, current.pm2_5_aqi.raw, current.pm2_5_aqi.formatted, day.windrose.banded, day.windrose.calm, unit.label.outTemp, unit.label.barometer, unit.label.rain, unit.label.rainRate, unit.label.windSpeed
 [StdReport]
    [[MQTTLoopDataReport]]
        # -------------------------------------------------------------------------------------------------------
        # Example report using  'MQTTLoopData'
        # Derived from, https://github.com/chaunceygardiner/weewx-loopdata
        #
        # -------------------------------------------------------------------------------------------------------
        enable = False
        skin = MQTTLoopData
        HTML_ROOT = mqttloopdata
        [[[Extras]]]
            [[[[mqtt]]]]
                enable = True
                #disconnect = 120
                cleanSession = true
                reconnect = true
                timeout = 30
                keepAliveInterval = 60

                useSSL = false
                #username =
                #password =
                host = localhost
                port = 9001
                [[[[[topics]]]]]
                    [[[[[[loopdata]]]]]]
"""

def loader():
    """ Load and return the extension installer. """
    return MQTTLoopDataPublisher()

class MQTTLoopDataPublisher(ExtensionInstaller):
    """ The extension installer. """
    def __init__(self):

        install_dict = {
            'version': VERSION,
            'name': 'MQTTLoopData',
            # add a leading space, so that long versions does not run into the description
            'description': ' Add loop data to the data being published to MQTT.',
            'author': "Rich Bell",
            'author_email': "bellrichm@gmail.com",
            'files': [('bin/user', ['bin/user/mqttloopdata.py',
                                    ]),
                      ('skins/MQTTLoopData', ['skins/MQTTLoopData/skin.conf',
                                              'skins/MQTTLoopData/index.html.tmpl',
                                              ]),
                      ('skins/MQTTLoopData/javascript', ['skins/MQTTLoopData/javascript/gauges.js',
                                                         'skins/MQTTLoopData/javascript/index.js',
                                                         'skins/MQTTLoopData/javascript/init.js.tmpl',
                                                         'skins/MQTTLoopData/javascript/mqtt.js.tmpl',
                                                         ]),
                      ],
        }

        mqttloopdata_dict = configobj.ConfigObj(StringIO(MQTTLOOPDATA_CONFIG))
        install_dict['config'] = mqttloopdata_dict

        super().__init__(install_dict)
