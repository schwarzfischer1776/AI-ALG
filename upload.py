import sys 

from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Disable OAuthlib's HTTPS verification when running locally.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# The file with your OAuth 2.0 credentials
client_secrets_file = 'JSON/client_secret.json'
scopes = ['https://www.googleapis.com/auth/youtube.upload']

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

#sys.path.append("ai-alg")
import story_to_movie_functor as movie_creator  


client_secrets_file = 'JSON/client_secret.json'
scopes = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('JSON/token.json'):
        creds = Credentials.from_authorized_user_file('JSON/token.json', scopes)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('JSON/token.json', 'w') as token:
            token.write(creds.to_json())

    return build('youtube', 'v3', credentials=creds)


def upload_video(youtube, file, title, description, category_id, keywords, privacy_status):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': keywords,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status
        }
    }

    media_body = MediaFileUpload(file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part='snippet,status', body=body, media_body=media_body)
    response = request.execute()

    video_id = response.get('id')
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    print(f'Video uploaded successfully: {video_url}')
    return video_url

def test_function(test):
    return "doppel bling"+ test 

def upload_to_youtube(filepath, story):
    basename = os.path.basename(filepath)
    story_list = movie_creator.parse_text_into_sentences(story)

    youtube = get_authenticated_service()
    url = upload_video(youtube, 'videos/' + basename , story_list[0], story, '22', ['keyword1', 'keyword2'], 'public')
    return url 

if __name__ == '__main__':
    #youtube = get_authenticated_service()
    # Replace with your video details
    #url = upload_video(youtube, 'output.mp4', 'Your Video Title', 'Your video description', '22', ['keyword1', 'keyword2'], 'public')
    #print(url)
    #file = movie_creator.parse_text_into_sentences("Bla. Bla. Bla")
    url = upload_to_youtube("/Users/felix/Documents/Informatics/Programming/hack_tum/story_creator/videos/2023-11-19_02-20-27_video.mp4", "After eating, Fluffy takes a nap in the sunny spot.")
    print(url) 

