import os
import requests
import firebase_admin

from firebase_admin import db
from firebase_admin import credentials
from googleapiclient.errors import HttpError
from ig_uploader import InstagramCrawler

from yt_uploader import initialize_upload


def uploadToYoutube(clipInfo, accessToken, tokenId):
    try:
        initialize_upload({
            "id": clipInfo["id"],
            "title": clipInfo["title"],
            "description": clipInfo["title"],
            "category": 22,
            "privacyStatus": "private",
            "keywords": "Twitch,highlights,short,video,funny"
        }, {
            "token": accessToken,
            "idToken": tokenId
        })

        db.reference('autoclip').child(
            clipInfo["id"]).update({'status': 'done'})
        os.remove(f"{clipInfo['id']}.mp4")
    except HttpError as e:
        print('An HTTP error %d occurred:\n%s', e.resp.status, e.content)

        os.remove(f"{clipInfo['id']}.mp4")
        db.reference('autoclip').child(
            clipInfo["id"]).update({'status': 'error'})


def onDataChange(event):
    print(f"Event {event.event_type} happened.")

    if event.event_type == 'put':
        for key in event.data:
            # Ignore status/connected_users patch
            if key in ["status", "connected_users"]:
                return

            clipInfo = event.data[key]
            downloadClip(clipInfo)

            for connectedUser in event.data[key]["connected_users"]:
                uploadToYoutube(
                    clipInfo, connectedUser["accessToken"], connectedUser["tokenId"])
                # upload to TikTok
                # upload to IG
                uploadToIG()


def downloadClip(clipInfo):
    print("Downloading clip...")

    response = requests.get(clipInfo['media_url'])

    open(f"{clipInfo['id']}.mp4", "wb").write(response.content)

    print("Clip saved.")


def uploadToIG():
    crawler = InstagramCrawler()

    try:
        crawler.auth()
    except:
        print("Auth failed.")
        return

    crawler.upload_video()

    print("Another one...")

    crawler.upload_video()


if __name__ == "__main__":
    # Firebase setup
    if not firebase_admin._apps:
        cred = credentials.Certificate('firebase.config.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://twitchsniffer-25e09.firebaseio.com'
        })

    db.reference('autoclip').listen(onDataChange)
