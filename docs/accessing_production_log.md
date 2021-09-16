Accessing production logs
-------------------------

Necessary when an error happens in production, that can not be
reproduced in the development server, and you need to figure out what
might have happened.

How it's setup
--------------

We use the default log setup for both Docker, Nginx and Django. This
means that all errors are logged to stdout/stderr in the two Docker
containers. These logs are received by Docker, which sends them to
journald on the host.

We can both access the logs through docker `docker logs` and through `journald` (see below)

How to access the logs
----------------------
Sudo access to the webserver is necessary. Here are the two commands
that you need to know:

Accessing Django log-file (e.g. django errors):
```
sudo journalctl CONTAINER_NAME=markedsspilletdk_web_1
```

Accessing Nginx webserver log-file (e.g. 404 errors, users access log):
```
sudo journalctl CONTAINER_NAME=markedsspilletdk_nginx_1
```
