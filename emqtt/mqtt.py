import logging

class mqtt_packet:
    def __init__(self, config):
        self.topic = config['MQTT_TOPIC']
        self.reset_time = config['MQTT_RESET_TIME']
        self.payload = config['MQTT_PAYLOAD']