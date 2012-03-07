rpush
=====

Python wrapper used to push notification to several web service

Currently support for:

 * BlackBerry

Planning to support, [see to do]
 
Since notification can work as background job, you can used rpush as job queue

What you need it is a Redis server (ver 2.4 using in development)
Also Need:

 * python redis
 * python web.py [optional]
 * python mako [optional]
 
Using python multiprocess to handle parallel job

Feature
=======

 * Modular (easy to separate jobs, via config use_module)

How To Use
==========

Create dummy config.ini file

    [main]
    #redis
    host=localhost
    port=6379
    db=0
    
    # max error log stored in redis
    max_log=3
    
    # max retry job failed
    max_retry=2
    
    worker=1
    # separated by space
    use_module=blackberry
    
    [blackberry]
    app_id = [YOUR-APP-ID]
    app_password = [YOUR-APP-PASSWORD]
    app_push_url = https://pushapi.eval.blackberry.com/mss/PD_pushRequest
    
Start worker

    $ cd /path/to/rpush
    $ python main.py config.ini
    
Easily send job queue via redis rpush method

    $ redis-cli
    $ > rpush jobs-blackberry "{\"pins\": [\"12345678\"], \"message\": \"Hi citra!\"}"
    
Easily monitoring log via redis-cli

    $ redis-cli
    $ # get latest failed job log and also the traceback
    $ > lrange failed-job 0 1
    $ # get latest sucess job log
    $ > lrange success-job 0 1
    $ # get job queue length, (blackberry push for example)
    $ > llen jobs-blackberry
    $ # see list of worker
    $ > HKEYS worker-info
    $ # see how many job has been worked by worker
    $ > GET worker-info [worker-id]
    $ # see how many job has been worked and failed by worker
    $ > GET worker-info-failed [worker-id]
    $ # see if your code already send wrong opcode/message
    $ > LRANGE invalid-message 0 100
    $ # see if your code already send wrong type
    $ > LRANGE invalid-type 0 100

Also you can easily monitoring job log via web interface,
to run weblog you need install web.py and mako template engine.

    $ sudo pip install web.py
    $ sudo pip install Mako

Or easily via setup.py:

    $ cd /path/to/rpush
    $ sudo python setup.py develop

Run web log, specify port in args 2, default 8080

    $ python weblog/weblog.py 13000

And open http://localhost:13000

TODO
====

 * complete weblog, support for modular report
 * easily launch new worker without dirty hand into console
 * support Android C2DM
 * support Apple APNS
 * support NGINX Push Stream Module
 * support Windows Mobile
 
Bug Reports
===========

Send your bug report, suggestion to rizky [at] abdi [dot] la

Credits
=======

 * Nicholas Brochu ![https://github.com/nbrochu], who originally write the library blackberry push in ruby
