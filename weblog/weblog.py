
import web
import redis
import os
import json

from ConfigParser import ConfigParser

from web.contrib.template import render_mako

render = render_mako(
    directories=[os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/')],
    input_encoding='utf-8',
    output_encoding='utf-8',
)

client = None

def _get_count():
    rv = {}

    rv['jobs'] = dict()
    rv['junk'] = dict()
    count_junk = 0
    for module in use_module.split():
        job_key = "jobs:" + module.lower()
        rv['jobs'][module] = client.llen(job_key)
        junk_key = "junk:" + job_key
        rv['junk'][module] = client.llen(junk_key)
        count_junk += rv['junk'][module]
        
    rv['count_success'] = client.llen('success:job')
    rv['count_failed'] = client.llen('failed:job')
    rv['count_invalid_message'] = client.llen('invalid:message')
    rv['count_worker'] = client.hlen('worker:info')
    rv['count_junk'] = count_junk
    rv['web_path'] = config.get('main', 'web_path')

    return rv

class Index(object):
    def GET(self):
        return render.index(title='Please select in menu', info=_get_count(), datas=[])
    
class Retry(object):
    def GET(self):
        
        data = dict()
        for module in use_module.split():
            data[module] = client.lrange('junk:jobs:' + module.lower(), 0, -1)
            
        return render.retry(title='Retry Jobs', info=_get_count(), data=data)
    
    def POST(self):
        wi = web.input()
        action = wi.action
        job = wi.job
        message = wi.message
        client.lrem('junk:jobs:' + job.lower(), message, 1)
        
        if action == "retry":
            message = json.loads(message)
            if not message.has_key("retried"):
                message["retried"] = 0
            message["retried"] += 1
            message = json.dumps(message)
            client.rpush('jobs:' + job.lower(), message)
        
        web.header("Content-Type", "application/json")
        return json.dumps(dict(ok=True))

class Latest(object):
    def GET(self, arg=None):
        if arg == 'failed':
            key = 'failed:job'
            title = 'Latest failed job'
        elif arg == 'success':
            key = 'success:job'
            title = 'Latest success job'
        elif arg == 'invalid:message':
            key = 'invalid:message'
            title = 'Latest invalid message'

        logs = client.lrange(key, 0, 100)
        return render.index(title=title, info=_get_count(), datas=logs)

class Worker(object):
    def GET(self, arg=None):
        datas = {}
        for w in client.hkeys('worker:info'):
            datas[w] = {}
            datas[w]['count_all'] = int(client.hget('worker:info', w))
            datas[w]['count_failed'] = int(client.hget('worker:info:failed', w))
            datas[w]['count_success'] = datas[w]['count_all'] - datas[w]['count_failed']
            
            worker_detail = client.hget('worker:info:detail', w)
            worker_detail = json.loads(worker_detail)
            state = "up" if worker_detail.get("state") else "down"
            serving = ",".join(worker_detail.get("ability", []))
            datas[w]['state'] = state
            datas[w]['serving'] = serving
            
            datas[w]['current_work'] = client.hget('worker:current_work', w)
            
        return render.worker(title='List worker info', info=_get_count(), datas=datas)

urls = (
    '/', 'Index',
    '/retry', 'Retry',
    '/latest/([a-z\-]+)', 'Latest',
    '/worker/([a-z]+)', 'Worker',
)


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')

    max_log = int(config.get('main', 'max_log'))

    rds_host = config.get('main', 'host')
    rds_port = config.get('main', 'port')
    rds_db = config.get('main', 'db')
    client = redis.Redis(host=rds_host, port=int(rds_port), db=int(rds_db))
    use_module = config.get('main', 'use_module')

    fvars = {
        'max_log': max_log,
        'client': client,
        'render': render,
        'Index': Index,
        'Latest': Latest,
        'Retry': Retry,
        'Worker': Worker
    }

    app = web.application(urls, fvars, autoreload=True)
    app.run()
    