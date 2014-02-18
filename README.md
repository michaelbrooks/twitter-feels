twitter-feels
=============

This is a Django web application that runs visualizations
of streaming data from Twitter.

There are three significant components:

1. A web interface that serves the visualizations.
2. A background process that streams tweets into the database.
3. Periodic aggregation and cleaning of the tweet data.

Setting up for Development
----------------

Below are instructions for setting up to develop this project.
Following that are additional instructions for production deployment.

### Prerequisites

Your system needs to have Git, Python 2.7, and Redis installed.
If you are on Linux, you can probably use your system package manager to install
most of this stuff.

First, use the [Set Up Git](https://help.github.com/articles/set-up-git) guide by GitHub to install Git on your system.

Next, you need to install Python 2.7 as well as `pip` and `virtualenv`, which
are used for managing python dependencies.
[This guide](http://python-guide.readthedocs.org/) has excellent instructions for
[Mac OS X](http://python-guide.readthedocs.org/en/latest/starting/install/osx/),
[Windows](http://python-guide.readthedocs.org/en/latest/starting/install/win/), and
[Linux](http://python-guide.readthedocs.org/en/latest/starting/install/linux/).

Finally, install Redis ([instructions](http://redis.io/download)).
The instructions are good for Linux. On Windows, download the zip archive for your system contained
in the [Windows port of Redis 2.6](https://github.com/MSOpenTech/redis/tree/2.6/bin/release).
Unzip the archive, and simply run `redis-server.exe` to start the server.

### Setting up the Project

Now that we have the prerequisites, you need to obtain a copy of the code.
Clone the repository to your machine:

```bash
$ git clone https://github.com/michaelbrooks/twitter-feels.git
$ cd twitter-feels
```


#### Create a virtual Python environment

Next, you need to create and activate a virtual Python environment just for this project:

```bash
$ virtualenv venv
$ source venv/bin/activate
```

This creates a directory called `venv` with a self-contained copy
of Python. You can customize packages here without affecting your
 system-wide Python installation.

*Important:* You must remember to activate this virtual environment in every terminal
where you are working on this project. Otherwise, you will be accidentally
using the global Python.

> *Windows:* If you are working on Windows, your activate command will look slightly different:
> ```bash
> # If you are using a bash shell on Windows:
> $ source venv/Scripts/activate
> # If you are using the Command Prompt on Windows:
> $ .\venv\Scripts\activate.bat
> ```

#### Install Python dependencies

The project depends on several additional Python packages.
These are listed with the required versions in the
[requirements/](https://github.com/michaelbrooks/twitter-feels/tree/master/requirements) directory.

You can install everything you need simply by running this command:

```bash
$ pip install -r requirements/dev.txt
```

Note that if you were setting up for production, you would use `requirements/prod.txt` instead.

#### Initialize database

Django can automatically initialize your database to put the application
in a runnable state:

```bash
$ ./manage.py syncdb
```

You will be asked to provide a username and password for an "admin" user.
Just make up something you can remember. It doesn't have to be secure.

For development, we are using a SQLite3 database. This will automatically be created
at `twitter_feels/default.db`, and will not be checked into the repository.
This prevents you from needing to worry about setting up a separate
DBMS in your development environment.

#### Launch the application

That's just about it. You should start the Django development web server with
 this command in order to complete the remaining configuration:

```bash
$ ./manage.py runserver
```

You should now be able to log into the Django admin site at
[http://localhost:8000/admin](http://localhost:8000/admin)
using the admin credentials you created a moment ago.

You can also visit the application itself at
[http://localhost:8000](http://localhost:8000)

Click on the `Status` button to view the status of the various back-end components.
You can see that most of them are stopped. Below are instructions
for setting up and running these services.

#### Configure Twitter streaming

In order to stream tweets, you need to provide your Twitter
API credentials and set some filter terms for streaming with.

First, create an app for your development environment at https://apps.twitter.com.
Just to be sure, provide `http://127.0.0.1:8000/` for the Website and Callback URL.
Once you have created the app, go to the "API Keys" tab to obtain your API keys.
Make sure to authorize the app for your own Twitter account to get an Access token and token secret.

Next, add a new set of [Twitter API Credentials](http://localhost:8000/admin/streamer/twitterapicredentials/add)
in the Django Admin site. Provide your name and email, as well as the API key/secret and access token/secret.

You also need to provide at least one filter term to use for streaming tweets.
Add a new [Filter Term](http://localhost:8000/admin/streamer/filterterm/add) in the Django Admin site.
For example, you may want to add `i feel` or some other term.

Next, to start streaming, you can run this command in a separate terminal
(don't forget to activate your Python virtual environment first):

```bash
$ ./manage.py stream --scheduler-queue=default
```

You can also run the command with a specific set of Twitter API credentials:

```bash
$ ./manage.py stream YOUR_NAME --scheduler-queue=default
```

The `--scheduler-queue` flag tells the streaming process to additionally manage
 scheduled tasks in your Redis Queue.

Now, if you visit the [Status Page](http://localhost:8000/status), you should
 see that the "Scheduler" is now running. You can also see your streaming process
 under "Twitter Streaming".

#### Launch background workers

At this point, tweets are going into your database, but you
have no process for actually processing them.

The analysis tasks are scheduled to be periodically run, so you
just need to start a worker process to run these tasks.
In another terminal (with virtual environment activated), simply run:

```bash
$ manage.py rqworker
```

> *Windows:* The basic Workers don't work properly on Windows for various
> reasons. You must use this command instead:
> ```bash
> $ manage.py rqworker --worker-class rq_win.WindowsWorker
> ```

Now, the [Status Page](http://localhost:8000/status) should show
that you have a Worker process running.

#### Launch Checklist

To summarize the above, in order to launch the application,
you need to ensure Redis is running, and then
run the following commands in *separate* terminals
with the virtual Python environment activated:

```bash
$ ./manage.py runserver
$ ./manage.py stream --scheduler-queue=default
$ ./manage.py rqworker [--worker-class rq_win.WindowsWorker]
```

Deployment Instructions
---------------

* Full instructions pending *

You need a MySQL server and a Redis server configured for production use.

Make sure to install the production requirements:

```code
$ pip install -r requirements/prod.txt
```

Make sure the environment variables referenced in the [production settings
file](https://github.com/michaelbrooks/twitter-feels/tree/master/twitter_feels/settings/prod.py)
are correctly (and securely) set.

Use an actual web server instead of the built in Django web server.
