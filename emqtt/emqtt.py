import signal
import logging
import email
import os
import time
from datetime import datetime
from email.policy import default
from paho.mqtt import publish

from emqtt.plugins import EmailProcessor
from emqtt.mqtt import mqtt_packet


log = logging.getLogger('emqtt')

class EMQTTHandler:
    def __init__(self, loop, config):
        self.config = config
        self.loop = loop
        self.reset_time = self.config['MQTT_RESET_TIME']
        self.handles = {}
        self.quit = False
        signal.signal(signal.SIGTERM, self.set_quit)
        signal.signal(signal.SIGINT, self.set_quit)
        if self.config['SAVE_ATTACHMENTS']:
            log.info('Configured to save attachments')


    async def handle_DATA(self, server, session, envelope):
        log.debug('Message from %s', envelope.mail_from)
        email_message = email.message_from_bytes(
          envelope.original_content, 
          policy=default
        )
        
        log.debug(
            'Message data (truncated): %s',
            email_message.as_string()[:250]
        )
        
        # If enabled this saves the message content as a string to disk
        # this is only useful for debugging or recording messages to 
        # be used in tests
        if self.config['SAVE_RAW_MESSAGES']:
            msg_filename = email_message['subject']
            log.debug( "Saving message content: %s", msg_filename )
            file_path = os.path.join('messages', msg_filename)
            with open(file_path, 'w+') as f:
                f.write( email_message.as_string() )
        
        # Check the dynamic plugins
        actions = EmailProcessor.get_plugins()
        log.debug( "Loaded processor plugins: %s", actions )
        mqtt_msg = None
        for plugin in actions:
            result = plugin.apply_to_sender( email_message['from'] )
            log.debug( "%s -> %s", plugin, result )
            if result is False:
                continue
                
            mqtt_msg = plugin.mqtt_message( email_message )
            
        self.mqtt_publish( mqtt_msg.topic, mqtt_msg.payload )

        # Save attached files if configured to do so.
        if self.config['SAVE_ATTACHMENTS'] and (
                # Don't save them during rese time unless configured to do so.
                mqtt_msg.topic not in self.handles
                or self.config['SAVE_ATTACHMENTS_DURING_RESET_TIME']):
            log.debug(
                'Saving attachments. Topic "%s" aldready triggered: %s, '
                'Save attachment override: %s',
                    mqtt_msg.topic,
                    mqtt_msg.topic in self.handles,
                    self.config['SAVE_ATTACHMENTS_DURING_RESET_TIME']
            )
            for att in email_message.iter_attachments():
                # Just save images
                if not att.get_content_type().startswith('image'):
                    continue
                filename = att.get_filename()
                image_data = att.get_content()
                file_path = os.path.join('attachments', filename)
                log.info('Saving attached file %s to %s', filename, file_path)
                with open(file_path, 'wb') as f:
                    f.write(image_data)
        else:
            log.debug('Not saving attachments')
            log.debug(self.handles)


        # Cancel any current scheduled resets of this topic
        if mqtt_msg.topic in self.handles:
            self.handles.pop(mqtt_msg.topic).cancel()

        if self.reset_time:
            # Schedule a reset of this topic
            log.debug( "Sheduling reset in %ds for %s", self.reset_time, mqtt_msg.topic )
            self.handles[mqtt_msg.topic] = self.loop.call_later(
                self.reset_time,
                self.reset,
                mqtt_msg.topic
            )
        return '250 Message accepted for delivery'

    def mqtt_publish(self, topic, payload):
        log.info('Publishing "%s" to %s', payload, topic)
        try:
            publish.single(
                topic,
                payload,
                hostname=self.config['MQTT_HOST'],
                port= self.config['MQTT_PORT'],
                auth={
                    'username': self.config['MQTT_USERNAME'],
                    'password': self.config['MQTT_PASSWORD']
                } if self.config['MQTT_USERNAME'] else None
            )
        except Exception as e:
            log.exception('Failed publishing')

    def reset(self, topic):
        log.info(f'Resetting topic {topic}')
        self.handles.pop(topic)
        self.mqtt_publish(topic, self.config['MQTT_RESET_PAYLOAD'])

    def set_quit(self, *args):
        log.info('Quitting...')
        self.quit = True