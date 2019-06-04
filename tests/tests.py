import unittest

import emqtt
import email
from email.policy import default
from emqtt import emqtt
from emqtt.mqtt import mqtt_packet
from emqtt.config import config
from emqtt.plugins import EmailProcessor

class EmailParsingTests(unittest.TestCase): 

  @classmethod
  def setUpClass(cls):
    cls.plugins = EmailProcessor.get_plugins()
    with open( "tests/data/test_email_1", "rb" ) as f:
      cls.msg_test_email_1 = email.message_from_binary_file(f, policy=default)    

  def test_load_default(self):
    """Load the plugins and ensure the last one is the default"""
    assert len( self.plugins ) >= 1
    self.assertIsInstance( self.plugins[-1], EmailProcessor )

    
  def test_mqtt_message_generation(self):
    """
    Parse an email with the default processor and validate the
    resulting mqtt message.
    """
    mqtt_msg = None
    for plugin in self.plugins:
        result = plugin.apply_to_sender( self.msg_test_email_1['from'] )

        if result is False:
            continue

        mqtt_msg = plugin.mqtt_message( self.msg_test_email_1 )

    assert mqtt_msg.topic == "emqtt/IPCamera <cam4_c2local.domain.com>"
    assert mqtt_msg.payload == "ON"
