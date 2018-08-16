# SteemQA Server

This is the backend server for the SteemQA application

The server consists of two services:
* The SteemQA REST server
* The SteemQA scraper

As its name suggests, the first service provides a REST API to SteemQA clients and the SteemQA scraper.
SteemQA persistent information is stored in a database on the server.
The SteemQA REST server is implemented using Django and the rest framework.

The SteemQA scraper periodically queries the Steemd nodes to retrieve SteemQA discussions and comments and
organize this information in a manner suitable for the SteemQA application.
