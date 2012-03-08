
import sys
import os
import signal
from multiprocessing import Process
from ConfigParser import ConfigParser

from jobseeker import Jobseeker

def parse_config(file_path):
    config = ConfigParser()
    config.read(file_path)
    
    new_conf = {}
    for key, value in config.items('main'):
        new_conf[key] = value
    
    new_conf['module'] = new_conf['use_module'].split()
    for service in new_conf['module']:
        new_conf[service] = {}
        if config.has_section(service):
            for key, value in config.items(service):
                new_conf[service][key] = value

    return new_conf

def signal_handler(signum, frame):
    global processes
    for p in processes:
        p.terminate()

if __name__ == '__main__':
    
    processes = []
    uname = os.uname()[1]
    config = parse_config(sys.argv[1])
    
    for pnum in xrange(int(config['worker'])):
        unemployed = Jobseeker(config, identity="%s-%d" % (uname, pnum))
        p = Process(target=unemployed.looking)
        p.start()
        processes.append(p)
        
    signal.signal(signal.SIGTERM, signal_handler)
    