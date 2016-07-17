import httplib2
import sys

from apiclient.discovery import build
from apiclient.http import MediaIoBaseUpload

from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from io import BytesIO, StringIO
scope = 'https://www.googleapis.com/auth/drive'

# Create a flow object. This object holds the client_id, client_secret, and
# scope. It assists with OAuth 2.0 steps to get user authorization and
# credentials.

def get_drive_service(client_id, client_secret):
  flow = OAuth2WebServerFlow(client_id, client_secret, scope)

  storage = Storage('credentials.dat')

  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, tools.argparser.parse_args())

  http = httplib2.Http()
  http = credentials.authorize(http)
  return build('drive', 'v3', http=http)

def update_csv_file(drive_service, file_id, content):
    return drive_service.files().update(fileId=file_id,
        body={'mimeType':'application/vnd.google-apps.spreadsheet'},
        media_body=MediaIoBaseUpload(BytesIO(content),
                                     mimetype='text/csv')).execute()

def update_csv_stream(drive_service, file_id, stream):
    return drive_service.files().update(fileId=file_id,
        body={'mimeType':'application/vnd.google-apps.spreadsheet'},
        media_body=MediaIoBaseUpload(stream,
                                     mimetype='text/csv')).execute()

def create_csv_file(drive_service, title, content, parents=[]):
    return drive_service.files().create(
        body={'name': title, 'mimeType':'application/vnd.google-apps.spreadsheet', 'parents': parents},
        media_body=MediaIoBaseUpload(BytesIO(content),
                                     mimetype='text/csv')).execute()

def create_raw_file(drive_service, title, content, parents=[]):
    media_body=MediaIoBaseUpload(BytesIO(content.encode('UTF-8')),
                                 mimetype='text/plain')
    return drive_service.files().create(
        body={'name': title, 'mimeType':'text/plain', 'parents': parents},
        
        media_body=media_body).execute()

def update_raw_file(drive_service, file_id, content):
    return drive_service.files().update(fileId=file_id,
        media_body=MediaIoBaseUpload(BytesIO(content.encode('UTF-8')),
                                     mimetype='text/plain')).execute()

def create_csv_stream(drive_service, title, stream, parents=[]):
    return drive_service.files().create(
        body={'name': title, 'mimeType':'application/vnd.google-apps.spreadsheet', 'parents': parents},
        media_body=MediaIoBaseUpload(stream,
        mimetype='text/csv')).execute()


def get_raw_file(drive_service, file_id):
    return drive_service.files().get_media(fileId=file_id).execute()  

def get_csv_file(drive_service, file_id):
    return drive_service.files().export(fileId=file_id, mimeType='text/csv').execute()  

def find_file_id_by_name(drive_service, name):
    resp = drive_service.files().list(q="name = '{}'".format(name)).execute()
    if 'files' in resp:
        return resp['files'][0]['id'] if len(resp['files']) > 0 else None
    else:
        raise Error('Failed listing files')