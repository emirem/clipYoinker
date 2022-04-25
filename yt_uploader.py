#!/usr/bin/python3

import os
import time
import random
import httplib2
import http.client

import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1
# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
                        http.client.IncompleteRead, http.client.ImproperConnectionState,
                        http.client.CannotSendRequest, http.client.CannotSendHeader,
                        http.client.ResponseNotReady, http.client.BadStatusLine)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_VERSION = 'v3'
API_SERVICE_NAME = 'youtube'
VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')

GOOGLE_CLIENT_ID = os.environ.get(
    "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_ID is not set.")
GOOGLE_CLIENT_SECRET = os.environ.get(
    "GOOGLE_CLIENT_SECRET", "GOOGLE_CLIENT_SECRET is not set.")


# Authorize the request and store authorization credentials.
def get_authenticated_service(args):
    credentials = google.oauth2.credentials.Credentials(
        args["token"],
        None,
        args["idToken"],
        'https://accounts.google.com/o/oauth2/token',
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET
    )
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def initialize_upload(clipInfo, authInfo):
    tags = None
    if clipInfo["keywords"]:
        tags = clipInfo["keywords"].split(',')

    body = dict(
        snippet=dict(
            title=clipInfo["title"],
            description=clipInfo["description"],
            tags=tags,
            categoryId=clipInfo["category"]
        ),
        status=dict(
            privacyStatus=clipInfo["privacyStatus"]
        )
    )
    youtube = get_authenticated_service(authInfo)

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting 'chunksize' equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(
            f"{clipInfo['id']}.mp4", chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.


def resumable_upload(request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print('Uploading file...')
            status, response = request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print('Video id "%s" was successfully uploaded.' %
                          response['id'])
                else:
                    exit('The upload failed with an unexpected response: %s' % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status,
                                                                     e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = 'A retriable error occurred: %s' % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit('No longer attempting to retry.')

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print('Sleeping %f seconds and then retrying...' % sleep_seconds)
            time.sleep(sleep_seconds)
