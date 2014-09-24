
import sys
import os
import signal
import logging
from multiprocessing import Process, Value
from ctypes import c_bool
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
        service = service.lower()
        new_conf[service] = {}
        if config.has_section(service):
            for key, value in config.items(service):
                new_conf[service][key] = value

    return new_conf

def signal_handler(signum, frame):
    global processes, unemployed
    unemployed.value = False
    for process in processes:
        process.join()

if __name__ == '__main__':
    
    processes = []
    uname = os.uname()[1]
    config = parse_config(sys.argv[1])
    
    logger = logging.getLogger("worker")
    logger.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    logger.info("INIT RPUSH Worker")
    unemployed = Value(c_bool, True)
    
    for pnum in xrange(int(config['worker'])):
        unemployed_worker = Jobseeker(config, logger,
            identity='%s-%d' % (uname, pnum), pnum=pnum+1, ppid=os.getpid())
        p = Process(target=unemployed_worker.looking, args=(pnum, unemployed))
        p.start()
        processes.append(p)
        
    
    signal.signal(signal.SIGTERM, signal_handler)
    