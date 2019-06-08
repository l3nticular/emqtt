import logging
from emqtt.mqtt import mqtt_packet
from emqtt.plugins import EmailProcessor

log = logging.getLogger('test_email_plugins_TestPlugin1')

class alpha_load_order_E(EmailProcessor):
    def apply_to_sender( self, sender ):
        log.debug( sender )
        return sender in ["A", "B", "C", "D", "E"]

    def mqtt_message( self, email_message ):
        response = mqtt_packet()
        response.topic = '{}/{}'.format(
          response.topic, 
          "E"
        )
        return response