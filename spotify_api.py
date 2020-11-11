#!C:/Python27/python.exe
#print("Content-Type: text/html\n")

import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


# Initializes the api
def initializeSpotipy():
    global m_spotify
    spotify_cred_manager = SpotifyClientCredentials(client_id = 'ccbd80aa17ee45749b1c5a23c204170e', client_secret = 'dd11692b597f4d59b8af73b2acaa6b2d')
    m_spotify = spotipy.Spotify(client_credentials_manager = spotify_cred_manager)


# Returns embed URL for spotify song.
def getEmbedURL(query):
    song = getSongItem(query)
    
    songID = song['id']
    embedURL = "https://open.spotify.com/embed/track/%s" % songID
		
    return embedURL
    

# Gets the top songs from Spotify's top playlist.    
# int_number : refers to the number of songs to return.
def getTopSongs(int_number): 
    
    top_tracks = m_spotify.playlist_tracks('37i9dQZF1DXcBWIGoYBM5M')
    top_10 = []

    for track in top_tracks['items'][:int_number]:
        
        top_10.append(track['track']['artists'][0]['name'] + " - " + track['track']['name'])
    
    return top_10



# Returns as strings artist, title
def querySong(query):
    song = getSongItem(query)
    if(song == 'null'):
        return 'null', 'null'
    str_artist = str(song['artists'][0]['name']).strip()
    str_title = str(song['name']).strip()
    
    return str_artist, str_title


# Returns the first spotipy track returned from 
# the given query.
# If nothing was found, empty string ("") is returned.
# NOTES
# Not sure if empty string will work for no returns. Haven't tested yet.
def getSongItem(query):
    error_message = "null"
    song = ""
    try:
        songSearch = m_spotify.search(q = query, type='track')
        bln_success = True
    except:
        bln_success = False
    finally:
        if(bln_success == False):
            return error_message

    items = songSearch['tracks']['items']
	
    # Make sure something was returned. If so, grab first item.
    if( len(items) > 0 ):
        song = items[0]
    else:
        return error_message;
    
    return song;
    