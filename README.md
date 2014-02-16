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
