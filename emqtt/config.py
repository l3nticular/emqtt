import logging
import os

log = logging.getLogger('emqtt.config')

def get_application_config():
    defaults = {
        'SMTP_PORT': 1025,
        'SMTP_LISTEN_ADDRESS': '0.0.0.0',
        'MQTT_HOST': 'localhost',
        'MQTT_PORT': 1883,
        'MQTT_USERNAME': '',
        'MQTT_PASSWORD': '',
        'MQTT_TOPIC': 'emqtt',
        'MQTT_PAYLOAD': 'ON',
        'MQTT_RESET_TIME': 20,
        'MQTT_RESET_PAYLOAD': 'OFF',
        'SAVE_ATTACHMENTS': 'True',
        'SAVE_ATTACHMENTS_DURING_RESET_TIME': 'False',
        'SAVE_RAW_MESSAGES': 'False',
        'LOG': 'True',
        'DEBUG': 'False'
    }

    config = {
        setting: os.environ.get(setting, default)
        for setting, default in defaults.items()
    }

    # Boolify
    for key, value in config.items():
        if value == 'True':
            config[key] = True
        elif value == 'False':
            config[key] = False
            
    # Convert to ints where appropriate
    int_configs = ['SMTP_PORT', 'MQTT_PORT', 'MQTT_RESET_TIME']
    for key in int_configs:
        config[key] = int(config[key])
        
    return config

# Load the config globally for now
config = get_application_config()
