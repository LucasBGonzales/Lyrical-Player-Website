from flask import Flask, render_template, request, url_for, session
import lyrics_api as lyr_api
import images_api as img_api
import spotify_api as spt_api
import database as db
import logger as log
import time as tm
app = Flask(__name__)
app.secret_key = "abc"

global m_blnInitialized
m_blnInitialized = False


def initialize():
    if(m_blnInitialized == False):
        # Set logger
        log.setDebug(True)
        
        # Initialize APIs
        db.initialize()
        spt_api.initializeSpotipy()
        
        # Update Top User Queries
        updateTopUserQueries(10)
        
        # Load top artist's image.
        top_songs = db.getTopUserQuery(1)[0]
        if(len(top_songs) > 0):
            songID = db.getTopUserQuery(1)[0]
            loadImageToSession(songID)
        
        # Initialize Flag
        initilized = True
    
    # Check Spotify Top List Update
    updateSpotifyTopList()
    updateTopSpotifySongs(10)

@app.route('/enter_lyrics', methods = ['POST','GET'])
def enter_lyrics():
    # Initialize 
    initialize()
    
    return render_template('enter_lyrics.html')
    
    
@app.route('/submit_lyrics', methods = ['POST','GET'])
def submit_lyrics():
    # Initialize 
    initialize()
    
    log.debug(f"flask_host.submit_lyrics:")
    
    # Get Lyrics from POST
    str_lyrics = request.form["txtLyrics"]
    log.debug(f"flask_host.submit_lyrics: Returned - {str_lyrics}")
    
    # Modify - Implement SQL Escapes.
    str_lyrics = lyr_api.cleanUpForSQL(str_lyrics)
    
    # Get Artist and song from session
    str_artist = session['strArtist']
    str_song = session['strSong']
    
    # Set lyrics in database based on songid collected from artist and song
    songID = db.getSongID(str_artist, str_song)
    db.setLyrics(songID, str_lyrics)
    
    # Commit changes.
    db.commitDatabase()
    
    return getQueryTemplate(str_artist, str_song)

@app.route('/')
def run():
    # Initialize 
    initialize()
    
    log.debug("flask_host.run():")
    
    return render_template('lyrical_player.html')
    


@app.route('/query', methods = ['POST','GET'])
def query():
    # Initialize 
    initialize()
    
    log.debug("flask_host.query(): ")

    lyr_result = ""
    img_result = ""
    spt_result = ""
    
    log.debug("flask_host.query(): Request artist and song from HTML")
    
    # Get Query
    if("v_query" in request.form):
        str_query = request.form["v_query"]
        log.debug(f"flast.host.query(): str_query = {str_query}")
        
        # Get song and artist
        str_artist = ""
        str_song = ""
        
        log.debug("flask_host.query(): Get query query from Spotify")
        # Get from Spotify
        str_artist, str_song = spt_api.querySong(str_query)
        log.debug(f"flask_host.query(): Arist, Song: {str_artist}, {str_song}")
        
        # Set session variables
        session['strArtist'] = str_artist
        session['strSong'] = str_song
    else:
        str_artist = session['strArtist']
        str_song = session['strSong']
    
    return getQueryTemplate(str_artist, str_song)


def getQueryTemplate(str_artist, str_song):
    search_term = f"{str_artist} {str_song}"
    
    # Handle Null
    if(str_artist == 'null' and str_song == 'null'):
        render_template("lyrical_player.html")
    
    # Get songID
    # SONGID TESTING
    log.debug("flask_host.getQueryTemplate(): Getting songID")
    songID = db.getSongID(str_artist, str_song)
    
    # Attempt to Get Lyrics
    log.debug("flask_host.getQueryTemplate(): Getting Lyrics")
    lyr_result = db.getLyrics(songID)
    
    # If Lyrics not found
    if(lyr_result == 'null'):
        get_lyr = lyr_api.getLyrics(str_artist, str_song)
        
        if(get_lyr != "null"):
            
            # Modify - Implement SQL Escapes.
            get_lyr = lyr_api.cleanUpForSQL(get_lyr)
            
            if(get_lyr == ""):
                log.debug("flask_host.getQueryTemplate(): get_lyr returned empty string.")
            else:
                log.debug(f"flask_host.getQueryTemplate(): Lyrics Returned: \n {get_lyr}")
                db.setLyrics(songID, get_lyr)
                lyr_result = db.getLyrics(songID)
        else:
            lyr_result = "No Lyrics Found"
      

    # Attempt to loag image to session.
    loadImageToSession(songID)
    
    
    # Attempt to get Spotify embed
    log.debug("flask_host.getQueryTemplate(): Getting Spotify embed URL")
    spt_result = db.getSpotifyEmbedURL(songID)
    
    # If not found, get from api, place in database
    if(spt_result == 'null'):
        log.debug("flask_host.getQueryTemplate(): Spotify embed not found in database")
        get_spt = spt_api.getEmbedURL(str_artist + " " + str_song)
        db.setSpotifyEmbedURL(songID, get_spt)
        spt_result = db.getSpotifyEmbedURL(songID)
        
        
    # Count user query
    db.countUserQuery(songID)

    
    # Update Top User Queries
    updateTopUserQueries(10)
    
    # Commit changes.
    db.commitDatabase()
    
    return render_template("lyrical_player.html", lyricsResult = lyr_result, spotifyURL = spt_result)



# Load Image to Session.
def loadImageToSession(int_songID):
    # Attempt to get Images
    log.debug("flask_host.getQueryTemplate(): Getting Images")
    img_result = db.getImageURL(int_songID)
    
    log.debug(f"flask_host.getQueryTemplate(): Image URL from DB: '{img_result}'")
    # If not found in database, get from api and place into database.
    if(img_result == 'null' or img_result == ""):
        log.debug("flask_host.getQueryTemplate(): Using img_api")
        
        str_artist, str_song = db.getArtistAndSong(int_songID)
        if(str_artist == 'null'):
            get_url=""
        else:
            get_url = img_api.getImageURL(str_artist)
            
        log.debug(f"flask_host.getQueryTemplate(): get_url: '{get_url}'")
        if(get_url == ""):
            log.debug("flask_host.getQueryTemplate(): Failed to get URL")
        else:
            db.setImageURL(int_songID, get_url)
            img_result = db.getImageURL(int_songID)
    
    session["imgResult"] = img_result



# Update session variables for top spotify songs.
def updateTopSpotifySongs(int_count):
    log.debug("flask_host.updateTopSpotifySongs(): ")
    
    # Set the Strings in session variables.
    for x in range(1, 11):
        log.debug(f"flask_host.updateTopSpotifySongs(): x = {x}")
        # Get songID
        songID = db.getSpotifyRankID(x)
        
        # Get artist, song
        str_artist, str_song = db.getArtistAndSong(songID)
        
        # Create session variable name
        str_sessionName = "ts_" + str(x)
        
        # Build String
        str_result = f"{str_artist} — {str_song}"
        log.debug(f"flask_host.updateTopSpotifySongs(): {str_result}")
        
        # Set Variable
        if(str_result.find('null') < 0):
            session[str_sessionName] = str_result

    
    



# Update session variables for top user queries.
def updateTopUserQueries(int_count):
    log.debug("flask_host.updateTopUserQueries(): ")
    
    # Get songIDs of top user queries
    arr_songIDs = db.getTopUserQuery(int_count)
    
    # Get the artist and songs for each songID.
    # Format it as artist, song.
    # Null results are ignored.
    for x in range(len(arr_songIDs)):
        # Create session variable name
        str_sessionName = "uq_" + str(x+1)
        
        # Get artist and song
        str_artist, str_song = db.getArtistAndSong(arr_songIDs[x])
        
        # Get query count
        int_queries = db.getUserQuery(arr_songIDs[x])
        
        # Build String
        #OLD str_result = str(int_queries) + ": " + str_artist + ", " + str_song
        str_result = str_artist + " - " + str_song
        log.debug(f"flask_host.updateTopUserQueries(): {str_result}")
        
        # Set Variable
        if(str_result.find('null') < 0):
            session[str_sessionName] = str_result




# Updates the Spotify Top List in the database
# if there is missing data or if data is outdated.
def updateSpotifyTopList():
    log.debug("flask.host.updateSpotifyTopList():")

    # Get time in seconds since epoch
    int_time = tm.time()
    
    bln_performUpdate = False
    
    # iterate through 1-10
    for x in range(1, 11):
        str_ret = db.getSpotifyRankID(x)
        
        # if return is 'null', update all from api
        if (str(str_ret) == 'null'):
            bln_performUpdate = True
            break
        else:
            int_songID = int(str_ret)
        
        # if date is 'null' or ((6*60*60) < time_difference), update all from api
        str_ret = db.getSpotifyRankTime(int_songID)
        
        # if return is 'null', update all from api
        if (str(str_ret) == 'null'):
            bln_performUpdate = True
            break
        else:
            int_updateTime = int(str_ret)
        
        int_currentTime = tm.time()
        int_timeDifference = int_currentTime - int_updateTime
        
        # Update every 6 hours. (Comparing seconds, hour * 60 * 60 to convert.)
        if ( (6*60*60) < int_timeDifference):
            bln_performUpdate = True
            break
    
    # Perform update if conditions met
    if(bln_performUpdate == True):
        log.debug("flask.host.updateSpotifyTopList(): Updating DB")
        arr_topSongs = spt_api.getTopSongs(10)
        
        # For each song
        for x in range(len(arr_topSongs)):
            # Get artist, song
            str_artist, str_song = spt_api.querySong(arr_topSongs[x])
            if(str_artist == 'null' and str_song == 'null'):
                continue
            log.debug(f"flask.host.updateSpotifyTopList(): Artist, Song: {str_artist}, {str_song}. X={x}")
            
            # Get songID
            songID = db.getSongID(str_artist, str_song)
            
            str_time = str(tm.time())
            int_time = int(str_time[0 : str_time.find(".") ])
            
            # Place in DB
            db.setSpotifyTopList(x+1, songID, int_time)



    

# Returns the next value in mycursor
def getCursorReturn():
    str_return = ""
    return str(mycursor.fetchone()[0])
    
    

# Easy SQL execute
# Create a single string with all your ocmmends, send it
# to this function to execute all of them.
# WARNING will not work if a ';' is used as anything
# other than a statement termination
def run_SQL(command):
    log.debug("flask_host.run_SQL(): Executing Commands");
    commands = command.split(";")
    for e in commands:
        e = e+";"
        if(e.strip() != ";"):
            mycursor.execute(e) #This executes a line of code in SQL


# Lets us run the app from this python file, as opposed to a bat file.
if __name__ == '__main__':
    app.run(debug=True)