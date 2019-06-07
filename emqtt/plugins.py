import os
import importlib
import logging
from emqtt.mqtt import mqtt_packet
from emqtt.config import config

import email.utils

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
        response = mqtt_packet( config )
        
        # Try to pull only the email out of the email
        # if that fails use what ever is in from.
        name,address = email.utils.parseaddr( email_message['from'] )
        if not address:
            address = email_message['from']
        
        response.topic = '{}/{}'.format(
          response.topic, 
          address.replace('@', '')
        )
        return response
        
    def attachment_hook( self, email_message ):
        return

class PluginManager:
    
    def _import_class(self, modulename, classname):
        ''' Returns imported class. '''
        try:
            return getattr(__import__(modulename, globals(), locals(), [classname], 0), classname)
        except AttributeError:
            log.error( 'Error in importing class. "%s" has no class "%s"', modulename, classname )
            return None
        except ImportError as e:
            log.error( 'Error in importing class: %s', e )
            return None
    
    def load_plugins( self, path=config['PLUGIN_DIRECTORY'] ):
        log.debug( "Plugin path: %s", path)
        
        plugin_module = path.replace( "/", "." )
        log.debug( "Plugin module: %s", plugin_module )
        
        plugin_files = [f for f in os.listdir(path) if f.endswith('.py')]
        
        # The Class in the file is assumed to be the same as the name of 
        # the file with out the .py extension.
        for plugin_file in plugin_files:
            plugin_class = plugin_file[:-3]
            plugin_path = os.path.join( path, plugin_file )
            log.debug( "Attempting to load '%s' from '%s'", plugin_class, plugin_module )
            
            # We don't need result other than to verify load, since just loading
            # the class will register the plugin.
            result = self._import_class( plugin_module, plugin_class)
            
            if result is None:
                log.warn( "Failed to load '%s' from '%s'", plugin_class, plugin_module )

