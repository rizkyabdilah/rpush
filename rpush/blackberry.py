
import random
import time
import datetime
import base64

import httputils    

class Blackberry(object):
    
    app_id = None
    app_password = None
    app_push_url = 'https://pushapi.eval.blackberry.com/mss/PD_pushRequest'
    BOUNDARY = "--boundary--"
    CRLF = "\r\n"
    
    def __init__(self, app_id, app_password, app_push_url=None):
        self.app_id = app_id
        self.app_password = app_password
        if app_push_url is not None:
            self.app_push_url = app_push_url
    
    def push(self, pins=[], message='', *args, **kwargs):
        
        if not isinstance(pins, (tuple, list)):
            pins = pins.split(',')
            
        pins = map(lambda p: p.strip(), pins)
        
        header = {
            'User-Agent': 'PyBBPush 0.1',
            'Content-type': "multipart/related; boundary={boundary}; type=application/xml; charset=us-ascii".format(boundary=self.BOUNDARY),
            'Authorization': "Basic %s" % base64.b64encode("%s:%s" % (self.app_id, self.app_password)),
            'Pragma': 'no-cache'
        }
        
        body = self.build_pap(pins, message)
        
        return httputils.post(self.app_push_url, body, header)
    
    def build_pap(self, pins, message):        
        address = ''
        for pin in pins:
            address += '<address address-value="{pin}" />'.format(pin=pin)
        
        bodys = ['--{boundary}',
                 'Content-Type: application/xml; charset=us-ascii',
                 '',
                 '<?xml version="1.0"?>',
                 '<!DOCTYPE pap PUBLIC "-//WAPFORUM//DTD PAP 2.1//EN" "http://www.openmobilealliance.org/tech/DTD/pap_2.1.dtd">',
                 '<pap>',
                 '<push-message push-id="{push_id}" deliver-before-timestamp="2020-08-13T07:41:59Z" source-reference="{app_id}">',
                 address,
                 '<quality-of-service delivery-method="confirmed" />',
                 '</push-message>',
                 '</pap>',
                 '--{boundary} ',
                 'Content-Type: text/plain; charset=us-ascii',
                 '', # extra line to match bb server
                 '{message}',
                 '--{boundary}--']
        
        push_id = random.randrange(1, 130) * 8 * 19 + 92
        body = self.CRLF.join(bodys).format(app_id=self.app_id,
                       push_id=push_id,
                       boundary=self.BOUNDARY,
                       message=message) + "\n\n"
        return body
