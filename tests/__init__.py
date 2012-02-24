
import unittest
from main import *

class BaseTestCase(unittest.TestCase):
    pass

def setUp():
    BaseTestCase.config = parse_config('test.ini')
    
def tearDown():
    pass
    