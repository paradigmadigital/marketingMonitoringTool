marketingMonitoringTool
=======================

Implementation for the youtube API to manage and monitor multiple channels.

Running
=======

You can run your starter application with:

  python multiple_channel_sample.py

It will ask how many accounts you want to check.

Please read sample.py carefully, it contains detailed information
in the comments.

Installation
============

It is recommended to use virtualenv in order to install dependencies.

After installing virtualenv, simply run:

  pip install -r requirements.txt


Documentation
=============

The documentation for the google-api-python-client library is avialable here:

    https://developers.google.com/api-client-library/python/start/get_started
   
   
Register a new application:

    https://developers.google.com/youtube/analytics/registering_an_application
   
To make this sample run you will need to populate the client_secrets.json file found at:

    https://cloud.google.com/console/project/apps~rugged-airway-455/apiui/credential

For more information about the client_secrets.json file format, please visit:

    https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
   
The YouTube Analytics API provides a single method that lets you retrieve different Analytics reports. Each request must use query parameters to specify a channel ID or content owner, a start date, an end date, and at least one metric. You may also provide additional query parameters, such as dimensions, filters, or sorting instructions.

    https://developers.google.com/youtube/analytics/v1/#examples

