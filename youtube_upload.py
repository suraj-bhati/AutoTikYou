import json
import os
import requests
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from moviepy.editor import VideoFileClip
import sys

def extract_details_from_json(filename: str) -> dict:
    print("Extracting details from JSON file...")
    with open(filename, 'r') as file:
        data = json.load(file)
        
        nwm_video_url_HQ = data.get('video_data', {}).get('nwm_video_url_HQ', 'Not Found')
        unique_id = data.get('author', {}).get('unique_id', 'Not Found')
        desc = data.get('desc', 'Not Found')
        
        print(f"Extracted details: URL - {nwm_video_url_HQ}, Unique ID - {unique_id}, Description - {desc}")
        return {
            'nwm_video_url_HQ': nwm_video_url_HQ,
            'unique_id': unique_id,
            'desc': desc
        }

def download_video(video_url: str, filename: str):
    print(f"Downloading video from {video_url}...")
    response = requests.get(video_url, stream=True)
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"Video downloaded and saved as {filename}")

def check_video_length(filename: str) -> bool:
    print(f"Checking video length for {filename}...")
    with VideoFileClip(filename) as video:
        video_length = video.duration
        print(f"Video length: {video_length} seconds")
        return video_length <= 59.99

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

def upload_video_to_youtube(filename: str, description: str, title: str) -> bool:
    print(f"Preparing to upload video: {filename}")
    if check_video_length(filename):
        print("Video length is within YouTube Shorts limits. Proceeding to upload.")
        youtube = authenticate_youtube()
        print("YouTube API authenticated.")
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
        print(f"Video uploaded successfully with ID {response['id']}")
        os.remove(filename)
        print(f"Deleted video file: {filename} after successful upload.")
        return True
    else:
        print("The video is too long for YouTube Shorts. Skipping upload.")
        os.remove(filename)
        print(f"Deleted video file: {filename}")
        return False

# Constants
CREDENTIALS_FILE = "youtube_credentials.json"

# Script execution
if __name__ == "__main__":
    print("Starting script execution...")
    details = extract_details_from_json("data.json")
    video_filename = f"{details['unique_id']}.mp4"
    download_video(details['nwm_video_url_HQ'], video_filename)
    description = f"{details['desc']} by {details['unique_id']}"
    title = details['desc'][:95]  # Limit to 95 characters

    if upload_video_to_youtube(video_filename, description, title):
        sys.exit(0)  # Exit with 0 for successful upload
    else:
        sys.exit(1)  # Exit with 1 for skipped upload

    print("Script execution completed.")
