import pytest

import os
import emqtt
import email


from email.policy import default
from emqtt import emqtt
from emqtt.mqtt import mqtt_packet
from emqtt.config import config
from emqtt.plugins import EmailProcessor
from emqtt.plugins import PluginManager

EMAIL_FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_data',
    )

PLUGINS_FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'test_plugin_suites',
    )

@pytest.fixture(autouse=True)
def plugins():
  return EmailProcessor.get_plugins()
  
# @pytest.fixture(autouse=True)
# def msg_test_email_1(datadir):
#   path = os.path.join( datadir, test_email_1)
#   with open( path, "rb" ) as f:
#     return email.message_from_binary_file(f, policy=default)



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
    for plugin in plugins:
        result = plugin.apply_to_sender( email_msg['from'] )

        if result is False:
            continue

        mqtt_msg = plugin.mqtt_message( email_msg )

    assert mqtt_msg.topic == "emqtt/cam4_c2local.domain.com"
    assert mqtt_msg.payload == "ON"
  
  
def test_dynamic_loading():
  """
  Verify there are plugins loaded after loading them dynamically
  """
  plugin_path = os.path.join( "tests", "test_plugin_suites", "test_email_plugins")
  PluginManager().load_plugins( path = plugin_path )
  assert len(EmailProcessor.get_plugins()) > 1
      
