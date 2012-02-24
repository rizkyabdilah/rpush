
from rpush.blackberry import Blackberry
from tests import *

class AllTests(BaseTestCase):
    
    def setUp(self):
        bbconf = self.config['blackberry']
        self.bbpush = Blackberry(bbconf['app_id'], bbconf['app_password'])
        self.pins = ["12345678", "87654321"]
        self.message = "test message"
    
    def tearDown(self):
        pass
    
    def test_build_pap(self):
        
        # should accept array of pin
        pap = self.bbpush.build_pap(self.pins, self.message)
        self.assertTrue(self.pins[0] in pap)
        self.assertTrue(self.pins[1] in pap)
        self.assertTrue(self.message in pap)
        
    def test_push(self):
        response = self.bbpush.push(pins=self.pins, message=self.message)
        self.assertEquals(response['header']['Status'], '200 OK')
        self.assertTrue('request has been accepted' in response['body'])
        
        # should accept string separated comma
        response = self.bbpush.push(pins=','.join(self.pins), message=self.message)
        self.assertEquals(response['header']['Status'], '200 OK')
        self.assertTrue('request has been accepted' in response['body'])
        