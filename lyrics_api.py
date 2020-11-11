import re
import urllib.request
from bs4 import BeautifulSoup
import logger as log

 
# Get Lyrics
def getLyrics(artist,song_title):
    url = getUrl(artist, song_title)

    try:
        # Get HMTL content
        content = urllib.request.urlopen(url).read()

        # print("HTML CODE:\n" + str(content)) # DEBUG Show HTML code

        # Parse HTML
        soup = BeautifulSoup(content, 'html.parser')
        lyrics = str(soup)

        # Lyrics lies between up_partition and down_partition
        up_partition = '<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->'
        down_partition = '<!-- MxM banner -->'
        lyrics = lyrics.split(up_partition)[1]
        lyrics = lyrics.split(down_partition)[0]

        # Clean it up
        lyrics = lyrics.replace('<br>','').replace('</br>','').replace('<br/>','').replace('</div>','').replace('<i>','').replace('</i>','').strip()
        #lyrics = removeEnclosed(lyrics, "[", "]")
        return lyrics
    except Exception as e:
        log.debug('lyrics_api.getLyrics(): No Lyrics Found')
    return "null"


# Get AZLyrics URL
def getUrl(artist,song_title):
    artist = removeEnclosed(artist, "(", ")")
    song_title = removeEnclosed(song_title, "(", ")")
    
    log.debug(f"lyrics_api.getUrl: {artist}, {song_title}")
    
    # All lowercase
    artist = artist.lower().strip()
    song_title = song_title.lower().strip()
    
    # Remove all except alphanumeric characters from artist and song_title
    artist = re.sub('[^A-Za-z0-9]+', "", artist)
    song_title = re.sub('[^A-Za-z0-9]+', "", song_title)

    # Remove starting 'the' from artist e.g. the who -> who
    if artist.startswith("the "):
        artist = artist[3:]
    
    return "http://azlyrics.com/lyrics/"+artist+"/"+song_title+".html"



def cleanUpForSQL(str_lyrics):
    # Modify - Implement SQL Escapes.
    str_lyrics = str_lyrics.replace("\\","\\\\")
    str_lyrics = str_lyrics.replace("'","\\'")
    #str_lyrics = str_lyrics.replace("\"","\\\"")
    str_lyrics = str_lyrics.replace("\"","\\\"")
    str_lyrics = str_lyrics.replace("&amp;", "&")
    #str_lyrics = str_lyrics.replace(":","1").replace("[","2").replace("]","3")
    log.debug(f"lyrics_api.cleanUpForSQL(): Result = {str_lyrics}")
    
    return str_lyrics


# Removes all sections of a string enclosed with the given parameters. 
def removeEnclosed(str_arg, str_delimiter1, str_delimiter2):
    str_ret = str_arg
    while(str_ret.count(str_delimiter1) > 0 and str_ret.count(str_delimiter2) > 0):
        intStart = str_ret.index(str_delimiter1)
        intEnd = str_ret.index(str_delimiter2)
        
        if(intStart < intEnd):
            str_toRemove = str_ret[intStart:intEnd+1]
            str_ret = str_ret.replace(str_toRemove, "")
        else:
            break
    
    return str_ret
    
    
    
    
    
    
    
    
    
    
    
    