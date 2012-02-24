
import sys
import os
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
        for key, value in config.items(service):
            new_conf[service][key] = value

    return new_conf

def signal_handler(signum, frame):
    global processes
    for p in processes:
        p.terminate()

if __name__ == '__main__':
    worker = 4
    
    processes = []
    uname = os.uname()[1]
    config = parse_config(sys.argv[1])
    unemployed = Jobseeker(config, identity="%s-%d" %(uname, 1))
    unemployed.looking()
    
    '''for pnum in xrange(worker):
        redis_client = redis.Redis(host='localhost', port=6379)
        worker = Worker(redis_client)
        workers.append(worker)
        p = Process(target=worker.work, args=(pnum,))
        p.start()
        processes.append(p)'''

    #sleep(2)
    #for p in processes:
    #    p.terminate()