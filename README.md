Twitter Feelings Stream
=======================

This is a Django web application that runs visualizations
of streaming data from Twitter.

The project architecture has 6 major components:

1. A MySQL database that stores analysis results and tweets (temporarily).
2. A Redis database that queues background processing jobs.
3. A background worker process that executes jobs from the Redis database.
4. A streaming worker process that connects to the Twitter API to gather tweets.
5. A process that periodically schedules analysis jobs into the Redis queue.
6. A web server that delivers the visualizations to the end user.


Setting up for Development
----------------

Below are instructions for setting up a development environment for this project.


### Prerequisites

First, you need to download and install [Vagrant](http://www.vagrantup.com/downloads)
and [Virtualbox](https://www.virtualbox.org/wiki/Downloads).
Virtualbox will be used to host a Linux virtual machine in which this app will run.
Vagrant is a manager for virtual machines that makes them very easy to work with.

You will also need Git. GitHub has an [excellent guide](https://help.github.com/articles/set-up-git) to setting
this up, if your system does not come with it.

Now you need to obtain a copy of the code.
Clone the repository to your machine:

```bash
$ git clone https://github.com/michaelbrooks/twitter-feels.git
$ cd twitter-feels
```


### Initialize a VM

Next, initialize your Linux virtual machine using Vagrant:

```bash
# Don't forget to add 'default' here!
$ vagrant up default
```

This will download a Vagrant "base box" and use it to start up a Virtualbox VM.
You can read more about Vagrant [here](http://docs.vagrantup.com/).

After running `vagrant up default`, a Virtualbox window should appear,
where you will see the Linux boot messages.

An important feature of Vagrant is that it will set up a "synced folder" between
the `twitter-feels` directory on your "host" machine and the `/home/vagrant/twitter-feels`
directory on the VM. That means that if you change project files on either your machine
or the VM, the changes will be synced to the other machine.

After the machine is booted, Vagrant will go on to run a "provisioning" script,
which installs some needed software on the VM. This is done using [Puppet](http://puppetlabs.com/puppet/what-is-puppet).
If you should need to rerun these provisioning scripts for some reason later,
you can do this with the command `vagrant provision`.

If you want to gracefully shut down the VM, you can do so with `vagrant halt`.
The machine still exists, and may be booted again with `vagrant up default`.

You may destroy the VM permanently with `vagrant destroy`, but note
that anything on the server (such as the database) will also be lost.


### Viewing the Web Application

Once the VM is running and provisioning is complete, you can visit the
web page at [http://localhost:8080](http://localhost:8080).

The provisioning script should have created a Django "superuser"
account which you can use to log into the Django admin site at
[http://localhost:8080/admin](http://localhost:8080/admin).
The username is *vagrant* and the password is *vagrant*.

Once you are logged in as the admin account,
you can visit the [Status](http://localhost:8080/status) page
to check on various components of the project.


### Accessing the VM

To control the execution of the project, you should log into the VM.
You can use the convenient `vagrant ssh` command to easily SSH into the machine.

You can also SSH into the machine with other SSH clients (such as Putty), at
`localhost:2222` (username and password are `vagrant`).

Vagrant itself generates and uses an SSH key to log in, which you can locate
using the command `vagrant ssh-config` (look at the IdentityFile field in the output).
You can refer to this key in other programs that need SSH access to the VM if you
want to avoid the username/password.

Once the VM is started, you also have the ability to log in directly through
the Virtualbox window with the username `vagrant` and password `vagrant`.

> *Fabric commands:* Once you are SSHed into the machine, you can do many
> common tasks through the [Fabric](http://fabfile.org/) commands
> defined in `fabfile.py`. You can list all of the available Fabric commands with `fab -l`.
> These are intended to be run *on the virtual machine*.


### Configure Twitter streaming

In order to stream tweets, you need to provide your Twitter
API credentials and set some filter terms for streaming with.
These are stored in the MySQL database.

If you don't already have some Twitter API credentials to use,
you should create an app for your development environment at https://apps.twitter.com.
Once you have created the app, go to the "API Keys" tab to obtain your API keys.
Authorize the app for your own Twitter account to get an access token and token secret.

Next, add a new set of [Api keys](http://localhost:8080/admin/twitter_stream/apikey/add/)
in the Django Admin site. Provide your name and email, as well as the API key/secret and access token/secret.

You also need to provide at least one filter term to use for streaming tweets.
Add a new [Filter Term](http://localhost:8080/admin/twitter_stream/filterterm/add/) in the Django Admin site.
For example, you may want to add `i feel` or some other term.

The streaming process (which should already be running) will take note
of these additions and being streaming tweets.
After a few seconds, you should see this activity reflected
on the Status page under "Twitter Streaming".

> *Note:* If you want to avoid having to deal with adding your API Key in the future,
> you can use the command `fab dump_key` to write your API Key data to the `.twitter_api_key.json` file.
> Then, if you later have to restore it into the database again, just use `fab load_key`.


Editing Workflow
---------------

You can use whatever editor you like to modify the source code files
on your local machine. These will be synced to the `/home/vagrant/twitter-feels` folder
on the VM, where they are available for execution.

After editing the source code, you will need to restart
one or more processes on the VM for your changes to be reflected
(this does not apply to static assets, only Python files).

For example, if you change one of the Python files, such as
`twitter_feels/apps/demo_vis/views.py`, you would need
to restart the *web* process with `fab restart:web`.
The other processes don't care about this file, so they do not need to be restarted.
More details about processes are below.


### Controlling Processes

A running copy of this project consists of 4 Python processes (in addition
to the MySQL and Redis server processes). These are listed
in the `Procfile` and in the `supervisord.conf` file that is generated
during provisioning.

If you follow the default setup procedure, the provisioning script
will install [Supervisor](http://supervisord.org/) on your VM.
Supervisor is a tool for managing long-running processes.
It can be used to start and stop processes, and to make sure
that the processes are restarted when they crash or the machine reboots.

When the machine boots, Supervisor will be started. It will
read your `supervisord.conf` file and then start all of the
needed project processes automatically.

There are Fabric commands for many common process manipulations:

```bash
# Stop all project processes
$ fab stop

# Stop the web server process
$ fab stop:web

# Start all of the project processes
$ fab start

# Restart the worker process
$ fab restart:worker

# See list of processes and status
$ fab status

# Run the web process directly through the terminal (not through Supervisor)
# (this will stop Supervisor's version first)
$ fab run:web

# There are commands for scaling web and worker processes:
$ fab scale_web
$ fab scale_web:down
$ fab count_web
$ fab scale_worker:3
```

You may also work directly with the `supervisorctl` tool (part of Supervisor)
to manage your processes.



#### Logging

All of the processes write log files that will be created in
the `/home/vagrant/twitter-feels/logs` directory on the VM.
Note that they will be automatically synced onto your local
machine as well.

Through these files, you can watch the output of your
web, stream, worker, and scheduler processes.

If you wish to continuously monitor the output,
you can try something like this, after logging into the VM:

```bash
$ tail -f logs/web-1.log
```

There is a handy Fabric command to make this easier:

```bash
$ fab watch:web
$ fab watch:web.error
```

You can use `fab clear_logs` to empty all of the log files.


#### Django Development Web Server

By default, the web server process runs [Gunicorn](http://gunicorn.org/)
with requests proxied through [Nginx](http://wiki.nginx.org/Main).

If, for some reason, you wish to run the *development* web server
built in to Django, you can do that with the following command:

```bash
$ fab dev_web
```

The development webserver auto-reloads on file changes,
which can be convenient.


#### Adding Python Packages

If you need to add additional Python packages, you
will want to edit one of the files in the `requirements/` directory.

Packages can be installed into your Python environment using pip:

```bash
$ pip install some-package
```

You can refresh all of the Python packages (from `requirements/dev.txt`) with this command:

```bash
$ fab pip_refresh
```


#### Updating the Database Structure

When you change your model classes, you will need to update
your database structure to correspond. You can run
the following command to update the database:

```bash
$ fab updatedb
```

This combines Django's builtin `syncdb` command and South's `migrate`
command. If you have not explicitly enabled South migrations
on your app, then `syncdb` is the only
part that will have an effect on your updated model.
Unfortunatley, the `syncdb` command is only capable of *creating* new tables.
It will not alter tables when you change anything about your models.

Therefore, it is recommended that you go ahead and enable
South migrations for your app. Before doing this,
your database should be up-to-date relative to the model classes:

```bash
$ fab init_south:my_app_name
```

This will create a `migrations` directory inside your app folder.
It will also create an initial migration that just describes your initial
database schema.

After changing or adding models, run this command to auto-generate
a new schema migration:

```bash
$ fab new_migration:my_app_name
```

You can then look over the migration file
before running `fab updatedb` to apply it.

A nice tutorial about South is available [here](http://south.readthedocs.org/en/latest/tutorial/part1.html)
