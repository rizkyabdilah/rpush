rpush
=====

Python wrapper used to push notification to several web service
Currently support for:
 * BlackBerry

Planning to support:
 * Android
 * Windows Mobile
 * APNS (Apple)
 * NGINX Push Stream
 
Since notification can work as background job, you also can used rpush as job queue
What you need it is a Redis (ver 2.4 using in development)
Also Need:
 * python json
 * python redis
 * python
 
Using python multiprocess to handle parallel job

Usage
=====

Set config.ini file

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
    $ > rpush jobs "{\"pins\": [\"12345678\"], \"message\": \"Hi citra!\", \"type\": \"blackberry\"}"
    
Easily monitoring log via redis-cli

    $ redis-cli
    $ # get latest failed job log and also the traceback
    $ > lrange failed-job 0 1
    $ # get latest sucess job log
    $ > lrange success-job 0 1
    $ # get job queue length
    $ > llen jobs
    $ # see list of worker
    $ > HKEYS worker-info
    $ # see how many job has been worked by worker
    $ > GET worker-info [worker-id]
    $ # see how many job has been worked and failed by worker
    $ > GET worker-info-failed [worker-id]
    $ # see if your code already send wrong opcode/message
    $ > LRANGE invalid-message 0 100
    
TODO
====

 * add web interface for monitoring log
 * easily launch new worker without dirty hand into console
 * support other service (Android, Apple, Windows and NGINX Push Stream)
    