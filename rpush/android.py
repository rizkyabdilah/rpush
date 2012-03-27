
import httputils
from datetime import datetime

class Android(object):
    
    auth_token = None
    c2dm_client_login_url = 'https://www.google.com/accounts/ClientLogin'
    c2dm_push_url = 'https://android.apis.google.com/c2dm/send'
    
    def __init__(self, app_email, app_email_password, app_source='rpush-android.c2dm.push-1.0'):
        body = {
            'Email': app_email, 'Passwd': app_email_password,
            'accountType': 'google', 'service': 'ac2dm',
            # app source is a string to identify your application
            # the format is [COMPANY-NAME]-[APPLICATION-NAME]-[VERSION-ID]
            'source': app_source
        }
        
        resp = httputils.post(c2dm_client_login_url, body=body)
        if resp['header']['Status'].lower() != '200 ok':
            print resp
            raise Exception, 'Unknown response from Google'
        
        for token in resp['body'].split():
            if token.startswith('Auth'):
                self.auth_token = token[5:]
                return
        
        raise Exception, 'No Auth Token from Google'
        
    
    def push(self,
             registration_id='',
             collapse_key=None,
             data={},
             delay_while_idle=True
             *args, **kwargs):
        
        # set access token first
        header = {
            'Authorization': 'GoogleLogin Auth=' + self.auth_token,
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
    