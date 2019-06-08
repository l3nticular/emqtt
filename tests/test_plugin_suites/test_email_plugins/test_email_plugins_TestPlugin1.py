import logging
from emqtt.plugins import EmailProcessor

log = logging.getLogger('test_email_plugins_TestPlugin1')

class test_email_plugins_TestPlugin1(EmailProcessor):
    def apply_to_sender( self, sender ):
        log.debug( sender )
        return sender == "AAA IPCamera <cam4_c2@l.filby.co>"

    def mqtt_message( self, email_message ):
        response = mqtt_packet()
        response.topic = '{}/{}'.format(
          response.topic, 
          "test_topic"
        )
        return response