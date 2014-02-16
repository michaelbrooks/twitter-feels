twitter-feels
=============

This is a Django web application that runs visualizations
of streaming data from Twitter.

There are three important components:

1. A web interface that serves the visualizations.
2. A background process that streams tweets into the database.
3. Periodic aggregation and cleaning of the tweet data.

Setting up for Development
----------------

*Instructions pending*

Running an RQ worker on Windows:

```bash
$ manage.py rqworker --worker-class rq_win.WindowsWorker
```

Run the RQ scheduler process (this manages periodic analysis tasks).
This causes it to check for scheduled tasks every 20 seconds:

```bash
$ manage.py rqscheduler -i 20
```

Run the streamer with the `--scheduler-queue` option
to manage the RQ scheduler as part of the Twitter streaming process
(less processes to start and stop):

```bash
$ manage.py stream <credentials_name> --interval 20 --scheduler-queue default
```
