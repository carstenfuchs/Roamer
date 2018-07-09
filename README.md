# Roamer
A website for monitoring your Husqvarna automowers.

This project uses [pyhusmow](https://github.com/chrisz/pyhusmow) and [Django](https://www.djangoproject.com) to periodically fetch the current state of your Husqvarna automowers, record all states in a database and display them on a website.

It is not intended to mimic the features of the Husqvarna mobile apps for smartphone, but to complement them:

  - show status history (e.g. a timeline of mower activity over the past week),
  - show information in web browsers (i.e. also desktop browsers, not only mobile),
  - show multiple mowers on a singe page (no need to explicitly switch between them),
  - send e-mail (e.g. on errors).
 
