import json
import os
import googleapiclient.discovery
import requests
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

def extract_details_from_json(filename: str) -> dict:
    with open(filename, 'r') as file:
        data = json.load(file)
        
        nwm_video_url_HQ = data.get('video_data', {}).get('nwm_video_url_HQ', 'Not Found')
        unique_id = data.get('author', {}).get('unique_id', 'Not Found')
        desc = data.get('desc', 'Not Found')
        
        return {
            'nwm_video_url_HQ': nwm_video_url_HQ,
            'unique_id': unique_id,
            'desc': desc
        }

def download_video(video_url: str, filename: str):
    response = requests.get(video_url, stream=True)
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

CREDENTIALS_FILE = "youtube_credentials.json"

def save_credentials_to_file(credentials):
    """Save credentials to a file."""
    with open(CREDENTIALS_FILE, 'w') as file:
        file.write(credentials.to_json())

def load_credentials_from_file():
    """Load credentials from a file if it exists, otherwise return None."""
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as file:
            return Credentials.from_authorized_user_file(CREDENTIALS_FILE)
    return None

def authenticate_youtube():
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"
    CLIENT_SECRETS_FILE = "youtube.json"
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    credentials = load_credentials_from_file()
    
    if not credentials:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(port=8080, access_type='offline')
        save_credentials_to_file(credentials)
    elif credentials.expired and credentials.refresh_token:
        credentials.refresh(google.auth.transport.requests.Request())
        save_credentials_to_file(credentials)

    return googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def upload_video_to_youtube(filename: str, description: str, title: str):
    youtube = authenticate_youtube()
    tags = description.split()
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=MediaFileUpload(filename)
    )
    response = request.execute()
    print(f"Uploaded video with ID {response['id']}")

details = extract_details_from_json("data.json")
download_video(details['nwm_video_url_HQ'], f"{details['unique_id']}.mp4")
description = f"{details['desc']} by {details['unique_id']}"
title = details['desc'][:95]  # Limit to 95 characters
upload_video_to_youtube(f"{details['unique_id']}.mp4", description, title)

