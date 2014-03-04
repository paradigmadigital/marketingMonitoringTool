# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for YouTube Analytics API.
Usage:
$ python sample.py

You can also get help on all the command-line flags the program understands
by running:

$ python sample.py --help

"""

import argparse
import httplib2
import os
import sys
import sqlite3 as lite
import time

from datetime import datetime, timedelta
from apiclient import discovery
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client import file
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from oauth2client.client import flow_from_clientsecrets
from array import array

# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/590260946072/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# These OAuth 2.0 access scopes allow for read-only access to the authenticated
# user's account for both YouTube Data API resources and YouTube Analytics Data.
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
  "https://www.googleapis.com/auth/yt-analytics.readonly"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_ANALYTICS_API_SERVICE_NAME = "youtubeAnalytics"
YOUTUBE_ANALYTICS_API_VERSION = "v1"

REPORT_VALUE = 365
INIT_TIME = time.time()

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

%s

with information from the Developers Console
https://cloud.google.com/console

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS))

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/yt-analytics-monetary.readonly',
      'https://www.googleapis.com/auth/yt-analytics.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))

channels_metrics = {'views':'Views','comments':'Comments','likes':'Likes','subscribersGained':'Subscribers Gained','subscribersLost':'Subscribers Lost','shares':'Shares'}

def get_authenticated_services(args, account_number):
    flow = flow_from_clientsecrets(CLIENT_SECRETS,
      scope=" ".join(YOUTUBE_SCOPES),
      message=MISSING_CLIENT_SECRETS_MESSAGE)

    youtubes = []
    youtubes_analytics = []
    for account_num in range(account_number):
        storage = Storage("%s-oauth2-%d.json" % (sys.argv[0],account_num))
        credentials = storage.get()

        if not credentials or credentials.invalid:
            credentials = run_flow(flow, storage, args)

        http = credentials.authorize(httplib2.Http())

        youtubes.append(build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
              http=http))
        youtubes_analytics.append(build(YOUTUBE_ANALYTICS_API_SERVICE_NAME,
              YOUTUBE_ANALYTICS_API_VERSION, http=http))
    return (youtubes, youtubes_analytics)

def get_channel_id(youtube):
    channels_list_response = youtube.channels().list(
      mine=True,
      part="id"
    ).execute()
    return channels_list_response["items"][0]["id"]

def run_analytics_report(youtube_analytics, channel_id, options):
    # Call the Analytics API to retrieve a report. For a list of available
    # reports, see:
    # https://developers.google.com/youtube/analytics/v1/channel_reports
    analytics_query_response = youtube_analytics.reports().query(
      ids="channel==%s" % channel_id,
      metrics=options.metrics,
      start_date=options.start_date,
      end_date=options.end_date,
      max_results=options.max_results,
      sort=options.sort
    ).execute()

    print "Analytics Data for Channel %s" % channel_id

    for column_header in analytics_query_response.get("columnHeaders", []):
         print "%-20s" % column_header["name"],
    print

    for row in analytics_query_response.get("rows", []):
        for value in row:
            print "%-20s" % value,
        print
        
def prepare_parser(tipo):
    now = datetime.now()
    one_day_ago = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    one_year_ago = (now - timedelta(days=tipo)).strftime("%Y-%m-%d")
    argparser.add_argument("--metrics", help="Report metrics",
        default="views,comments,likes,shares,subscribersGained,subscribersLost")
    argparser.add_argument("--start-date", default=one_year_ago,
        help="Start date, in YYYY-MM-DD format")
    argparser.add_argument("--end-date", default=one_day_ago,
        help="End date, in YYYY-MM-DD format")
    argparser.add_argument("--max-results", help="Max results", default=10)
    argparser.add_argument("--sort", help="Sort order", default="-views")


def main(argv):
    #Number of channels
    account_number = int(raw_input('Youtube channels number? '))
    tipo = int(raw_input('Report days? '))

    prepare_parser(tipo)
    args = argparser.parse_args()

    try:
        (youtube, youtube_analytics) = get_authenticated_services(args,
                                                            account_number)
        try:
            for idx, val in enumerate(youtube):
                channel_id = get_channel_id(val)
                run_analytics_report(youtube_analytics[idx], channel_id, args)
        except HttpError, e:
            print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
    except client.AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
          "the application to re-authorize")

# For more information on the YouTube Analytics API you can visit:
#
# http://developers.google.com/youtube/analytics/
#
# For more information on the YouTube Analytics API Python library surface you
# can visit:
#
# https://developers.google.com/resources/api-libraries/documentation/youtubeAnalytics/v1/python/latest/
#
# For information on the Python Client Library visit:
#
# https://developers.google.com/api-client-library/python/start/get_started
if __name__ == '__main__':
    main(sys.argv)

