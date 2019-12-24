from __future__ import print_function
import pickle
import os.path
# Google API
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# Spotipy python for spotify API
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
# JSON
import json
import requests


class Credentials:
    def __init__(self, client_id, client_secret, redirect):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect = redirect

# Class for storing info about song from sheet api
class Track:
    def __init__(self, artist, album, song):
        self.artist = artist
        self.album = album
        self.song = song


# gets spotify credentials/client info for application from file


def createSpotifyCredentialsObj():
    with open('spotifyID.json') as json_file:
        data = json.load(json_file)
        for p in data['spotify']:
            creds = Credentials(
                p['client_id'], p['client_secret'], p['redirect_uri'])
    return creds


credentials = createSpotifyCredentialsObj()

SPOTIPY_CLIENT_ID = credentials.client_id
SPOTIPY_CLIENT_SECRET = credentials.client_secret
SPOTIPY_REDIRECT_URI = credentials.redirect
PLAYLIST_ID = '2K8kj2paBKlXqCueepH3Py'

client_credentials_manager = SpotifyClientCredentials(client_id=credentials.client_id,
                                                      client_secret=credentials.client_secret)
spotify = spotipy.Spotify(
    client_credentials_manager=client_credentials_manager)


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID of spreadsheet.
DEC_SHEET_ID = '1qNsUKvOKQtWUTX7tnoqIm9JGDHs6gpcMAeHcxgEZLGY'  # DECEMBER playlist
# range of cells for song info from the form
INFO_RANGE = 'Form Responses 1!C2:E'


def getTrackID(trackDict):
    track_id = ''
    for d in trackDict.values():
        # TODO: add validation of type and number of elements
        track_id = d.get('items')[0].get('id')
    return track_id

def notInPlist(tids, username, ):
    removeList = []

    return removeList

# TODO: remove tracks from songIDs if already in playlist
def removeDups(songIDs):
    return


def toSpotify(tracks):
    print('going to Spotify...')
    track_ids = []
    for track in tracks:
        searchResult = spotify.search(
            q='artist:' + track.artist + ' track:' + track.song, limit=1, offset=0, type='track')
        # convert search result to JSON string
        result = getTrackID(searchResult)
        track_ids.append(result)
    # got tids -> to playlist, prompt user for token
    username = 'KDVS Core'
    scope = 'playlist-modify-public'
    print("...getting tokens...")
    token = util.prompt_for_user_token(
        username, scope, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)
    if token:
        # if token exists, authorize and add tracks to playlist
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        # TODO: remove songs from playlist if not in list of tids
        # TODO: remove duplicates from track_ids before adding to playlist
        results = sp.user_playlist_add_tracks(
            username, playlist_id=PLAYLIST_ID, tracks=track_ids)
        print(results)
    else:
        print("cant get token for", username)


def getSheetInfo():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API & get info
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=DEC_SHEET_ID,
                                range=INFO_RANGE).execute()
    values = result.get('values', [])
    tracks = []
    # prints the values
    if not values:
        print('No data found.')
    else:
        print('Artist, Album, Song:')
        for row in values:
            # Print columns C, D, E, which correspond to indices 0, 1, 2
            print('%s, %s, %s' % (row[0], row[1], row[2]))
            tracks.append(Track(row[0], row[1], row[2]))
    return tracks


def main():
    tracks = getSheetInfo()
    toSpotify(tracks)


if __name__ == '__main__':
    main()
