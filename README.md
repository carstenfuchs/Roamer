# Roamer

A website for monitoring your Husqvarna automowers.

This project uses [pyhusmow](https://github.com/chrisz/pyhusmow) and [Django](https://www.djangoproject.com) to periodically fetch the current state of your Husqvarna automowers, record all states in a database and display them on a website.

It is not intended to mimic the features of the Husqvarna mobile apps for smartphones, but to complement them:

  - show status history (e.g. a timeline of mower activity over the past week),
  - show information in web browsers (i.e. also desktop browsers, not only mobile),
  - show multiple mowers on a single page (no need to explicitly switch between them),
  - send e-mail (e.g. on errors).
 
Note that this is not a ready-to-use program for end users that can easily be installed.
It requires at least basic knowledge of [Python](https://www.python.org) and [Django](https://www.djangoproject.com) to deploy it on a web server.


## Overview

The automowers (robots) periodically transfer their state via a mobile data connection to the Husqvarna servers.
From there, just as the smartphone apps, we regularly fetch the current mower states and store them in the database.
The database content is used to create the web pages.

Querying the mower states from the Husqvarna servers and storing them in our database is
is implemented as a Django management command, `query_Husqvarna`.
This script has two modes of operation that deserve a consideration:

If the script can regularly be run on a machine that has direct access to the project's database,
it can store the mower state directly and is done. This is the easiest and most reliable approach,
but not all hosting providers support `cron` jobs and outgoing connections to remote servers.

The alternative is to run `query_Husqvarna` on a different machine that is independent from the one
that hosts the web application: The script connects to and queries the states from
the Husqvarna servers normally.  Then it submits the data via a normal web form to
the web instance, whose form implementation takes the data and in turn writes it
into the local database.
