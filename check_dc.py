from datetime import date
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from tqdm import tqdm

CLIENT_FILE = 'client.json'
API_NAME='gmail'
API_VERSION='v1'
SCOPES=['https://mail.google.com/']

MAIL_HEADER='Hola! Mail enviado'
SENDER='experimento.mail.dc@gmail.com'

def gmail_authenticate():
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

# get the Gmail API service
service = gmail_authenticate()

#Buscar mails con el titulo correspondiente
result = service.users().messages().list(userId='me',q='From: {}'.format(SENDER)).execute()
all_msgs = []
if 'messages' in result:
    all_msgs.extend(result['messages'])
while 'nextPageToken' in result:
    page_token = result['nextPageToken']
    result = service.users().messages().list(userId='me',q=MAIL_HEADER, pageToken=page_token).execute()
    if 'messages' in result:
        all_msgs.extend(result['messages'])

dates_received = []
for msg in tqdm(all_msgs):
    msg = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
    headers = {l['name']: l['value'] for l in msg['payload']['headers']}
    if headers['From'] == SENDER:
        dates_received.append(headers['Date'])
        if headers['X-Spam-Flag'] != 'NO':
            print('Fijate en spam!')
        service.users().messages().delete(userId='me',id=msg['id']).execute()

if len(dates_received) == 0:
    print('Ups parece que no estan llegando mails...')
else:
    print('{} mails de prueba han llegado con exito. Los mismos han sido eliminados. Sus fechas son: {}'.format(len(dates_received), dates_received))

print(dates_received)