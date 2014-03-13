twitter-feels
=============

This is a Django web application that runs visualizations
of streaming data from Twitter.

The architecture includes 6 different components:

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

Now that we have the prerequisites, you need to obtain a copy of the code.
Clone the repository to your machine:

```bash
$ git clone https://github.com/michaelbrooks/twitter-feels.git
$ cd twitter-feels
```


### Initialize a VM

Next, initialize your Linux virtual machine using Vagrant:

```bash
$ vagrant up
```

This will download a Vagrant "base box" and use it to start up a Virtualbox VM.
The configuration for Vagrant is in the `Vagrantfile` and you can read more about
Vagrant [here](http://docs.vagrantup.com/).
After running `vagrant up`, a Virtualbox window should appear,
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
The machine still exists, and may be booted again with `vagrant up`.

You may destroy the VM permanently with `vagrant destroy`, but note
that anything on the server (such as the database) will also be lost.


### Viewing the Web Application

Once the VM is running and provisioning is complete, you can visit the
web page at [http://localhost:8080](http://localhost:8080).

The provisioning script should have created a Django "superuser"
account which you can use to log into the Django admin site at
[http://localhost:8080/admin](http://localhost:8080/admin).
The username is 'vagrant' and the password is 'vagrant.

Once you are logged in as the admin account,
you can visit the [Status](http://localhost:8080/status) page
to view the status of various components of the project.


### Configure Twitter streaming

In order to stream tweets, you need to provide your Twitter
API credentials and set some filter terms for streaming with.

First, create an app for your development environment at https://apps.twitter.com.
Once you have created the app, go to the "API Keys" tab to obtain your API keys.
Make sure to authorize the app for your own Twitter account to get an Access token and token secret.

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


Accessing the VM
----------------

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

Once you are SSHed into the machine, you can control the project
processes through a series of [Fabric](http://fabfile.org/) commands
defined in `fabfile.py`. For example:

```bash
# Stop all project processes
$ fab stop

# Stop the web server process
$ fab stop:web

# Start all of the project processes
$ fab start

# Restart the worker process
$ fab restart:worker
```

You can get the status of your processes with the command `fab status` and you can
list all of the available Fabric commands with `fab -l`.

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


#### Django Development Web Server

By default, the web server process runs [Gunicorn](http://gunicorn.org/)
with requests proxied through [Nginx](http://wiki.nginx.org/Main).

If, for some reason, you wish to run the *development* web server
built in to Django, you can do that with the following command:

```bash
$ fab dev_web
```

The development webserver features auto-reloading on file changes,
which can be convenient sometimes.


#### Adding Python Packages

If you need to add additional Python packages, you
will want to edit one of the files in the `requirements/` directory.

Packages can be installed into your Python environment using pip:

```bash
$ pip install some-package
```

You can refresh all of the requirements (from the `requirements/dev.txt` file) with this command:

```bash
$ fab pip_refresh
```


#### Updating the Database Structure

If you add a model, you will need to re-run Django's `syncdb`
command.

```bash
$ fab syncdb
```

> *Note:* Django *does not* support migrations normally. That is,
> if you change an existing model, it will not automatically update your database.
> However, `syncdb` works fine for newly-created models.
> You can manually make changes to your database, or you can drop
> the altered table manually and then re-add with `syncdb`.
> Eventually we should use [South](http://south.readthedocs.org/en/latest/index.html)
> to do migrations.
