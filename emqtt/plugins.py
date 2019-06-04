import logging
from emqtt.mqtt import mqtt_packet
from emqtt import config

log = logging.getLogger('emqtt')

####
# Base class for user-defined plugins
class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
            cls.default = cls
        else:
            # This must be a plugin implementation, which should be
            # registered. Simply appending it to the list is all that's
            # needed to keep track of it later.
            cls.plugins.append(cls)
            
    def get_plugins(cls, *args, **kwargs):
            return [p(*args, **kwargs) for p in (cls.plugins + [cls.default])]


class EmailProcessor(metaclass=PluginMount):
    """
    Super class for plugins that can process email messages to customize
    the MQTT topic, payload, reset-time as well as take any actions on
    attachments
    
    TODO: Figure out how to handle:
      * reset time (-1 for no reset)
      * Attachments
      * how to hook into email addresses.
    """
    
    def apply_to_sender( self, sender ):
        return True

    def mqtt_message( self, email_message ):
        response = mqtt_packet( config.get_application_config() )
        response.topic = '{}/{}'.format(
          response.topic, 
          email_message['from'].replace('@', '')
        )
        return response
        
    def attachment_hook( self, email_message ):
        return
    

class TestEmailProcessor(EmailProcessor):
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
