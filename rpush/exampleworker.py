
class ExampleWorker(object):
    
    def __init__(self, worker_redis, opt1):
        self.worker = worker_redis
        self.opt1 = opt1

    def work(self, param1, param2, **kwargs):
        ret = int(param1) + int(param2)
        return ret
