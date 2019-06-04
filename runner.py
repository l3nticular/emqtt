#!/usr/bin/env python3
import asyncio
import email
import logging
import os
import time
from datetime import datetime
from email.policy import default

from aiosmtpd.controller import Controller

from emqtt import emqtt
from emqtt import plugins
from emqtt.config import config


# Configure Logger
log = logging.getLogger('emqtt')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
level = logging.DEBUG if config['DEBUG'] else logging.INFO
log.setLevel(level)


if __name__ == '__main__':

    # Log to console
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    log.addHandler(ch)

    # If there's a dir called log - set up a filehandler
    if os.path.exists('log'):
        log.info('Setting up a filehandler')
        fh = logging.FileHandler('log/emqtt.log')
        fh.setFormatter(formatter)
        log.addHandler(fh)
        
    log.info(', '.join([f'{k}={v}' for k, v in config.items()]))

    loop = asyncio.get_event_loop()
    c = Controller(
        emqtt.EMQTTHandler(loop, config), 
        loop, 
        config['SMTP_LISTEN_ADDRESS'], 
        config['SMTP_PORT']
    )
    
    c.start()
    
    log.info('Running')
    
    try:
        while not c.handler.quit:
            time.sleep(0.5)
        c.stop()
    except:
        c.stop()
        raise
