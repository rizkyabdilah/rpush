
import traceback
import sys
import os
import redis
import json
import base64
from time import sleep
from datetime import datetime
from StringIO import StringIO

from worker import *

_get_class = lambda s: eval('%s' % s)

class Jobseeker(object):
    
    def __init__(self, config, logger, identity='no-identity', pnum=0, ppid=None):
        self.client = redis.Redis(host=config['host'], port=int(config['port']), db=int(config['db']))
        self.identity = identity
        self.max_log = int(config['max_log'])
        self.max_retry = int(config['max_retry'])
        
        self.ppid = ppid
        self.logger = logger
        self.einfo = {"identity": self.identity, "ppid": self.ppid}

        self.use_module = config['worker|%d' % pnum].split()
        self.abilities = {}
        for ability in self.use_module:
            lability = ability.lower()
            config[lability]["worker_redis"] = self.client
            self.abilities[lability] = _get_class(ability)(**config[lability])
            
        self.job_lists = map(lambda j: 'jobs:%s' % j.lower(), self.use_module)
        
        self.client.hincrby('worker:info', self.identity, 0)
        self.client.hincrby('worker:info:failed', self.identity, 0)
        
        # set state working
        self.logger.info("worker %d is up. ability: [%s]" %
                         (pnum, ', '.join(self.use_module)), extra=self.einfo)
        worker_info = {"ability": self.use_module, "state": True}
        self.client.hset("worker:info:detail", self.identity, json.dumps(worker_info))
        self.complete_current_work()
    
    def _dtnow(self):
        return datetime.today().strftime('%m-%d_%H:%M:%S-%s')
    
    def gen_jobid(self):
        return self._dtnow()
        
    def replied_num(self, jobid, incr=0):
        return self.client.hincrby("retry:job", jobid, incr)
        
    def got_fired(self):
        # set state down
        worker_info = self.client.hget("worker:info:detail", self.identity)
        if not worker_info:
            return
        worker_info = json.loads(worker_info)
        worker_info["state"] = False
        self.client.hset('worker:info:detail', self.identity, json.dumps(worker_info))
    
    def looking(self, pnum, unemployed):
        while unemployed.value:
            if self.ppid is not None and os.getppid() != self.ppid:
                
                self.logger.critical("worker is going down: %s", "parent is dead jim",
                                     extra=self.einfo)
                self.got_fired()
                
                sys.exit(2)

            # from pydev import pydevd; pydevd.settrace('localhost', port=8989, stdoutToServer=True, stderrToServer=True)
            raw_message = self.client.blpop(self.job_lists, 1)

            if raw_message is not None:
                self.logger.debug("worker got message: %s", raw_message, extra=self.einfo)
                self.set_current_work(raw_message)
                self.work(raw_message)
                self.complete_current_work()
                
        else:
            self.got_fired()
            self.logger.info("%s got permanently unemployed, restart worker" %
                self.identity)
        
    def work(self, raw_message):
        job_type, message = raw_message
        # kalau message yang di passing salah
        # job yang gagal tidak diantrikan
        try:
            job = json.loads(message)
        except Exception, e:
            self.logger.critical("worker got invalid message: %s", message, extra=self.einfo)
            self.failed(message, 'invalid:message')
            return

        # tambahkan job id
        # gunanya untuk retry job
        if job.get('jid') is None:
            job['jid'] = self.gen_jobid()
            self.logger.info("worker got new job for [%s], giving id %s, message %s",
                             job_type, job["jid"],message, extra=self.einfo)
        else:
            replied_num = self.replied_num(job['jid'])
            self.logger.info("worker got replied job, job id %s, replied num %d",
                             job['jid'], replied_num, extra=self.einfo)
        
        # tambahkan jam kerja worker
        self.client.hincrby('worker:info', self.identity, 1)
        try:
            ability_to_use = job_type.replace('jobs:', '')
            self.logger.debug("worker use ability %s",
                              ability_to_use, extra=self.einfo)
            response = self.abilities[ability_to_use].work(**job)
            
        except Exception, e:
            self.logger.warning("worker fail, job type: %s", ability_to_use, extra=self.einfo)
            
            traceback.print_exc(sys.exc_info()[2])
            ## self.logger.critical("exception message: %s %s", exc_info[0], e, extra=self.einfo)
            self.failed(job_type, json.dumps(job))
            return
        
        # assumed success without exception
        self.logger.info("worker success do the job, job id: %s, job type: %s",
                         job["jid"], job_type, extra=self.einfo)
        self.success(message, response)
    
    def success(self, message, response='ok'):
        dt = self._dtnow()
        tb_info = '''Worker: {id}\n\n
        Date: {dt}\n\n
        Message: {msg}\n\n
        Response: {rsp}
        '''.format(id=self.identity, dt=dt, msg=message, rsp=response)
        self.client.lpush('success:job', tb_info)
        self.client.ltrim('success:job', 0, self.max_log)
    
    def failed(self, job_type, message, failed_key='failed:job'):
        etype, evalue, etraceback = sys.exc_info()
        tb_io = StringIO()
        traceback.print_exception(etype, evalue, etraceback, limit=10, file=tb_io)
        dt = self._dtnow()
        # store exception value di redis
        # thread sebagai capped log 100
        tb_info = '''Worker: {id}\n\n
        Date: {dt}\n\n
        Message: {msg}\n\n
        Exception: {tb_value}
        '''.format(id=self.identity, dt=dt, msg=message, tb_value=tb_io.getvalue())
        self.client.lpush(failed_key, tb_info)
        self.client.ltrim(failed_key, 0, self.max_log)
        
        tb_io.close()
        
        if failed_key == 'failed:job':
            self.queue_again(job_type, message)
            
    def queue_again(self, job_type, message):
        # tambahkan informasi gagal kerja
        self.client.hincrby('worker:info:failed', self.identity, 1)
        job = json.loads(message)
        replied_num = self.replied_num(job["jid"], 1)
        if replied_num >= self.max_retry:
            self.logger.debug("job is fail more than max retry (%d), job_type: %s, message: %s",
                              self.max_retry, job_type, message, extra=self.einfo)

            # send failed job to trash can
            self.client.rpush('junk:%s' % job_type, message)
            return
        self.logger.debug("job %s is failed x times, but replied, max replied %d",
                          job_type, replied_num, self.max_retry, extra=self.einfo)
        
        self.client.rpush(job_type, message)
        
    def set_current_work(self, raw_message):
        self.client.hset('worker:current_work', self.identity, str(raw_message))
    
    def complete_current_work(self):
        self.client.hset('worker:current_work', self.identity, "idle")

