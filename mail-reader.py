from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import base64
import email
import oauth2client
from apiclient import errors
from oauth2client import client
from oauth2client import tools

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'PJN SPAM FILTER'


def get_credentials():
    print("Authorizing...")
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def ListMessagesMatchingQuery(service, user_id='me', query=''):
  print("Downloading e-mails list from Google server")
  try:
    response = service.users().messages().list(userId=user_id, q=query, maxResults=100, includeSpamTrash=True).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])
    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError, error:
    print('An error occurred: %s' % error)

def GetMessage(f, service, user_id, msg_id):
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    print("SPAM" in message.get("labelIds"), "\n\n")
    messData = {}
    messData['title'] = message['snippet']
    messData['body'] = "";
    if "parts" in message['payload']:
        for part in message['payload']["parts"]:
            if part["mimeType"] == "text/html":
                messData['body'] += saveToFileString(f, messData['body'], part)		
    else:
        if message['payload']["mimeType"] == "text/html":
            messData['body'] += saveToFileString(f, messData['body'], message['payload'])	
    spamState = "NIE"
    if "SPAM" in message.get("labelIds"):
       spamState = "TAK"
    mess_to_save = "$MESSAGE$ $%s$ %s\n" % (spamState, messData['body'])
    f.write(mess_to_save)
    
    return messData
  except errors.HttpError, error:
    print('An error occurred: %s' % error)

def saveToFileString(f, body, payload):
    try:
        msg_str = base64.urlsafe_b64decode(payload.get("body",[]).get("data",[]).encode('utf-8'))
        body += strip_tags(email.message_from_string(msg_str).as_string()).replace("\n"," ").replace("\r","")	
    except UnicodeDecodeError, error:
        return ""
    return body
    
def ReadAllMessages(file_, service, query):
    messages = ListMessagesMatchingQuery(service, "me", query)
    
    importedMessages=[]
    for i in range(len(messages)):
        importedMessages.append(GetMessage(file_, service, "me", messages[i].get("id",[])))
    print("Messages where saved to file.")
    return importedMessages

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    h = open('./corpus/test-final.txt','w')
    #ham = ReadAllMessages(h, service, "in:anywhere")
    #ham = ReadAllMessages(h, service, "")
    ham = ReadAllMessages(h, service, "")
    h.close()
if __name__ == '__main__':
    main()

