#!/usr/bin/env python3
import asyncio
import email
import logging
import os
import time
import ssl
from datetime import datetime
from email.policy import default

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult, LoginPassword

from emqtt import emqtt
from emqtt.config import config

# Configure Logger
log = logging.getLogger('emqtt')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
level = logging.DEBUG if config['DEBUG'] else logging.INFO
log.setLevel(level)

def auth_always_pass(server, session, envelope, mechanism, auth_data):
    return AuthResult(success=True, handled=True)

auth_db = {
    b"user1": b"password1",
    b"user2": b"password2",
    b"user3": b"password3",
}

# Name can actually be anything
def authenticator_func(server, session, envelope, mechanism, auth_data):
    # For this simple example, we'll ignore other parameters
    assert isinstance(auth_data, LoginPassword)
    username = auth_data.login
    password = auth_data.password
    # If we're using a set containing tuples of (username, password),
    # we can simply use `auth_data in auth_set`.
    # Or you can get fancy and use a full-fledged database to perform
    # a query :-)
    if auth_db.get(username) == password:
        return AuthResult(success=True)
    else:
        return AuthResult(success=False, handled=False)


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

    log.debug(', '.join([f'{k}={v}' for k, v in config.items()]))

    if os.path.exists('certificate.pem') and os.path.exists('key.pem'):
        log.info('Setting up TLS Context')
        tls_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        tls_context.check_hostname = False
        tls_context.load_cert_chain('certificate.pem', 'key.pem')
    else:
        tls_context = None

    loop = asyncio.get_event_loop()
    c = Controller(
        handler=emqtt.EMQTTHandler(loop, config),
        loop=loop,
        authenticator=auth_always_pass,
        auth_required=False,
        ssl_context=tls_context,
        auth_require_tls=False,
        hostname=config['SMTP_LISTEN_ADDRESS'],
        port=config['SMTP_PORT']
    )
    
    c.start()

    if False:
        logging.basicConfig(level=logging.DEBUG)
        mlog = logging.getLogger("mail.log")
        mlog.setLevel(logging.DEBUG)
        loop.set_debug(enabled=True)
    
    log.info('Running')
    
    try:
        while not c.handler.quit:
            time.sleep(0.5)
        c.stop()
    except:
        c.stop()
        raise
