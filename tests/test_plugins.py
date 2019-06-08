import pytest
import logging
import os
import emqtt
import email
from email.message import EmailMessage
from email.policy import default

from emqtt import emqtt
from emqtt.mqtt import mqtt_packet
from emqtt.config import config
from emqtt.plugins import EmailProcessor
from emqtt.plugins import PluginManager

log = logging.getLogger('plugin_test')

EMAIL_FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_data',
    )

PLUGINS_FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_plugin_suites',
    )

@pytest.fixture()
def plugins():
  return EmailProcessor.get_plugins()

# This fixture is an optional setup method
# that will clean out the plugins already loaded.
@pytest.fixture()
def clean_plugins():
  if hasattr( EmailProcessor, "plugins" ):
    EmailProcessor.plugins = []
  return None

def test_load_default(plugins):
  """Load the plugins and ensure the last one is the default"""
  assert len( plugins ) >= 1
  assert isinstance( plugins[-1], EmailProcessor )


@pytest.mark.datafiles(
  os.path.join( EMAIL_FIXTURE_DIR, "test_email_1")
  )
def test_mqtt_message_generation(plugins, datafiles):
  """
  Parse an email with the default processor and validate the
  resulting mqtt message.
  """
  for file in datafiles.listdir():
    email_msg = None
    with open( file, "rb" ) as f:
      email_msg = email.message_from_binary_file(f, policy=default)
      
    mqtt_msg = None
    plugin = PluginManager().get_plugin( email_msg['from'] )
    mqtt_msg = plugin.mqtt_message( email_msg )

    assert mqtt_msg.topic == "emqtt/cam4_c2local.domain.com"
    assert mqtt_msg.payload == "ON"
  
  
def test_dynamic_loading( clean_plugins ):
  """
  Verify there are plugins loaded after loading them dynamically
  """
  plugin_path = os.path.join( "tests", "test_plugin_suites", "test_email_plugins")
  PluginManager().load_plugins( path = plugin_path )
  
  plugins = EmailProcessor.get_plugins()
  assert len(plugins) > 1
  assert plugins[0].__class__.__name__ is 'test_email_plugins_TestPlugin1'
  assert plugins[1].__class__.__name__ is 'EmailProcessor'  


def test_dynamic_loading_with_class_name_mismatch( clean_plugins ):
  """
  At this point the plugin loader doesn't care if the classname 
  matches, during import of the file it will register and getting
  the specific class isn't important
  
  Maybe build in a safety check in the future that will prevent loading
  a plugin if the classname doesn't match.
  """

  plugin_path = os.path.join( "tests", "test_plugin_suites", "filename_class_mismatch")

  PluginManager().load_plugins( path = plugin_path )
  plugins = EmailProcessor.get_plugins()
  assert len(plugins) == 2
  assert plugins[0].__class__.__name__ is "TestPlugin1_Obvious_Misname"
  assert plugins[1].__class__.__name__ is 'EmailProcessor'



def test_plugin_alpha_load_order( clean_plugins ):
  """
  Verify there are plugins loaded after loading them dynamically
  
  There are a collection of plugins that are alpha ordered
  and each subsequent plugin can also match the plugins that 
  would have come before (in theory it should never get there
  because the earlier plugin would have caught it)
  
  Check order, then check the mqtt messages so they match the sender
  """

  plugin_path = os.path.join( "tests", "test_plugin_suites", "alpha_load_order")

  PluginManager().load_plugins( path = plugin_path )
  plugins = EmailProcessor.get_plugins()
  assert len(plugins) == 6
  assert plugins[0].__class__.__name__ is "alpha_load_order_A"
  assert plugins[1].__class__.__name__ is "alpha_load_order_B"
  assert plugins[2].__class__.__name__ is "alpha_load_order_C"
  assert plugins[3].__class__.__name__ is "alpha_load_order_D"
  assert plugins[4].__class__.__name__ is "alpha_load_order_E"
  assert plugins[5].__class__.__name__ is 'EmailProcessor'
  
  test_addresses = ["A", "B", "C", "D", "E", "default"]    
  
  for test_address in test_addresses:
    message = EmailMessage()
    message['from'] = test_address
    
    plugin = PluginManager().get_plugin( test_address )
    mqtt_message = plugin.mqtt_message( message )
    
    assert mqtt_message.topic == "emqtt/{0}".format( test_address )
      
