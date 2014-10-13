rpush
=====

This is a incomplete docummentation (todo: complete this)

Library for delayed job. Using redis as message broker.

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
    use_module=sendemail
    
    [sendemail]
    mandrill_api_key
    
    
Start worker

    $ cd /path/to/rpush
    $ python main.py config.ini
    
Easily send job queue via redis rpush method

    $ redis-cli
    $ > rpush jobs:sendemail "{\"to\": \"mail@example.com\", \"from\": \"sender@example.com\", \"subject\": \"Subject Test\", \"body_plain\": \"text message\"}"

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
 * support example library for common use-case delayed job
 
Bug Reports
===========

Send your bug report, suggestion to rizky [at] abdi [dot] la

