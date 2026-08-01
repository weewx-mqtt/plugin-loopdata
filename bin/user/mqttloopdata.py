import user.loopdata

class MQTTLoopData(user.loopdata.LoopData):
    # def __init__(self, engine, config_dict):
    def __init__(self, logger, name, plugin_dict, _mqtt_dict, _topics, weewx_dict):
        super(user.loopdata.LoopData, self).__init__(weewx_dict['engine'], weewx_dict['config_dict'])

    def get_callbacks(self):
        """ The callbacks. """

        return []

