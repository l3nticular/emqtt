import unittest

import emqtt
import email
from email.policy import default

def test_sum():
    assert sum([1, 2, 3]) == 6, "Should be 6"
    
def test_mqtt_message_generation():
  fp = open( "tests/messages/c2_alarm_2019529233933", "rb" )
  config = emqtt.get_application_config()
  msg = email.message_from_binary_file(fp, policy=default)    
  fp.close()
  c = emqtt.EMQTTHandler( None, config )
  mqtt_response = c.get_mqtt_message( msg, None )
  
  assert mqtt_response.topic == "emqtt/IPCamera <cam4_c2local.domain.com>"
  