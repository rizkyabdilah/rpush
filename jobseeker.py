
import traceback
import sys
import redis
import json
from time import sleep
from datetime import datetime
from StringIO import StringIO

from rpush import *

_get_class = lambda s: eval(s[0].upper() + s.lower()[1:])

class Jobseeker(object):
    
    def __init__(self, config, identity='no-identity'):
        self.client = redis.Redis(host=config['host'], port=int(config['port']), db=int(config['db']))
        self.identity = identity
        self.max_log = int(config['max_log'])
        self.max_retry = int(config['max_retry'])

        self.module = config['module']
        self.abilities = {}
        for ability in self.module:
            self.abilities[ability.lower()] = _get_class(ability)(**config[ability])
            
        self.job_lists = map(lambda j: 'jobs:%s' % j, self.module)
    
    def looking(self):
        while True:
            raw_message = self.client.blpop(self.job_lists, 1)

            if raw_message is not None:
                self.work(raw_message)
            sleep(1)
        
    def work(self, raw_message):
        job_type, message = raw_message
        # kalau message yang di passing salah
        # job yang gagal tidak diantrikan
        try:
            job = json.loads(message)
        except Exception, e:
            self.failed(message, 'invalid:message')
            return

        # tambahkan job id
        # gunanya untuk retry job
        if job.get('jid') is None:
            job['jid'] = datetime.today().strftime('%Y:%M:%d/%H-%m-%s.%S')
        
        # tambahkan jam kerja worker
        self.client.hincrby('worker:info', self.identity, 1)
        try:
            ability_to_use = job_type.replace('jobs:', '')
            response = self.abilities[ability_to_use].push(**job)
        except Exception, e:
            self.failed(job_type, json.dumps(job))
            return
        
        # assumed success without exception
        self.success(message, response)
    
    def success(self, message, response='ok'):
        tb_info = '''
        Worker: {id}\n\n
        Message: {msg}\n\n
        Response: {rsp}
        '''.format(id=self.identity, msg=message, rsp=response)
        self.client.lpush('success:job', tb_info)
        self.client.ltrim('success:job', 0, self.max_log)
    
    def failed(self, job_type, message, failed_key='failed:job'):
        etype, evalue, etraceback = sys.exc_info()
        tb_io = StringIO()
        traceback.print_exception(etype, evalue, etraceback, limit=10, file=tb_io)
        
        # store exception value di redis
        # thread sebagai capped log 100
        tb_info = '''
        Worker: {id}\n\n
        Message: {msg}\n\n
        Exception: {tb_value}
        '''.format(id=self.identity, msg=message, tb_value=tb_io.getvalue())
        self.client.lpush(failed_key, tb_info)
        self.client.ltrim(failed_key, 0, self.max_log)
        
        tb_io.close()
        
        if failed_key == 'failed:job':
            self.queue_again(job_type, message)
            
    def queue_again(self, job_type, message):
        # tambahkan informasi gagal kerja
        self.client.hincrby('worker:info:failed', self.identity, 1)
        job = json.loads(message)
        retry_count = self.client.hincrby('retry:job', job['jid'], 1)
        if retry_count >= self.max_retry:
            return
        
        self.client.rpush(job_type, message)

