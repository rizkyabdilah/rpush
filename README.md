rpush
=====

Python wrapper used to push notification to several web service

Currently support for:

 * BlackBerry
 * Android

Planning to support, [see to do]
 
Since notification can work as background job, you can use rpush as job queue via jobseeker.

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

Using rpush as library
--------------------

    >>> import rpush
    >>> # push to android c2dm
    >>> c2dm = rpush.android.Android(app_email=[APP-EMAIL], app_email_password=[APP-EMAIL-PASSWORD])
    >>> c2dm.push(registration_id=[REG-ID], collapse_key=None, data={"message": "Hi Citra!"}, delay_while_idle=True)
    >>> # push to blackberry
    >>> pushapi = rpush.blackberry.Blackberry([APP-ID], [APP-PASSWORD], [APP-PUSH-URL])
    >>> pushapi.push(pins=[12345678], message="Hi again Citra!")


Using jobseeker as Message Queue with rpush
-------------------------------------------

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
    use_module=blackberry android
    
    [android]
    app_email = [YOUR-EMAIL-ADDRESS]
    app_email_password = [YOUR-EMAIL-PASSWORD]
    app_source = [COMPANY-APPLICATION-VERSION]
    
    [blackberry]
    app_id = [YOUR-APP-ID]
    app_password = [YOUR-APP-PASSWORD]
    app_push_url = https://pushapi.eval.blackberry.com/mss/PD_pushRequest
    
    
Start worker

    $ cd /path/to/rpush
    $ python main.py config.ini
    
Easily send job queue via redis rpush method

    $ redis-cli
    $ > rpush jobs:android "{\"registration_id\": \"REG_ID\", \"collapse_key\": 123, \"data\": {\"message\": \"Hi citra!\"}}"
    $ > rpush jobs:blackberry "{\"pins\": [\"12345678\"], \"message\": \"Hello again citra!\"}"
    
Easily monitoring log via redis-cli

    $ redis-cli
    $ # get latest failed job log and also the traceback
    $ > lrange failed:job 0 1
    $ # get latest sucess job log
    $ > lrange success:job 0 1
    $ # get job queue length, (blackberry push for example)
    $ > llen jobs:blackberry
    $ # see list of worker
    $ > HKEYS worker:info
    $ # see how many job has been worked by worker
    $ > GET worker:info [worker-id]
    $ # see how many job has been worked and failed by worker
    $ > GET worker:info:failed [worker-id]
    $ # see if your code already send wrong opcode/message
    $ > LRANGE invalid:message 0 100
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

Notes
=====

 * You need to implicit your plugin library in rpush/__init__.py if you want to use your own library.

TODO
====

 * complete weblog, support for modular report
 * easily launch new worker without dirty hand into console
 * support Apple APNS
 * support NGINX Push Stream Module
 * support Windows Mobile
 
Bug Reports
===========

Send your bug report, suggestion to rizky [at] abdi [dot] la

Credits
=======

 * Nicholas Brochu ![https://github.com/nbrochu], who originally write the library blackberry push in ruby
