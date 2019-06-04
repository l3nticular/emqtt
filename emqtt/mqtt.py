import logging

from emqtt.config import config

class mqtt_packet:
    def __init__(self, config=config):
        self.topic = config['MQTT_TOPIC']
        self.reset_time = config['MQTT_RESET_TIME']
        self.payload = config['MQTT_PAYLOAD']