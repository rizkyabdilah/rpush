
import httputils
from datetime import datetime

class Android(object):
    
    c2dm_push_url = 'https://android.apis.google.com/c2dm/send'
    
    def __init__(self):
        pass
    
    def push(self,
             registration_id='',
             collapse_key=None,
             data={},
             delay_while_idle=True,
             auth_token=''
             *args, **kwargs):
        
        # set access token first
        header = {
            'Authorization': auth_token,
            'Pragma': 'no-cache'
        }
        
        body = {
            'registration_id': registration_id,
            'collapse_key': collapse_key
        }
        
        # id collapse key is not defined, then set it as current date (microtimestamp)
        if collapse_key is None:
            body['collapse_key'] = datetime.today().strftime('%Y:%M:%d/%H-%m-%s.%S')
        
        for k, v in data.iteritems():
            body['data.%s' % k] = v
         
        if delay_while_idle:
            body['delay_while_idle'] = 1
            
        return httputils.post(self.c2dm_push_url, body, header)
    