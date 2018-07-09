# Roamer
A website for monitoring your Husqvarna automowers.

This project uses [pyhusmow](https://github.com/chrisz/pyhusmow) and [Django](https://www.djangoproject.com) to periodically fetch the current state of your Husqvarna automowers, record all states in a database and display them on a website.

It is not intended to mimic the features of the Husqvarna mobile apps for smartphones, but to complement them:

  - show status history (e.g. a timeline of mower activity over the past week),
  - show information in web browsers (i.e. also desktop browsers, not only mobile),
  - show multiple mowers on a singe page (no need to explicitly switch between them),
  - send e-mail (e.g. on errors).
 
Note that this is not a ready-to-use program for end users that can easily be installed.
It requires at least basic knowledge of [Python](https://www.python.org) and [Django](https://www.djangoproject.com) to deploy it on a web server.
