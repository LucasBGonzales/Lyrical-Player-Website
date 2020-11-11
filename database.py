import mysql.connector
import logger as log


def initialize():
    # Initialize global variables.
    global m_mydb
    global m_cursor
    global m_connected
    # Try to connect to server
    try:
        m_mydb = mysql.connector.connect(
            host="localhost",       # Host. IP for remote server, localhost for local server
            user="root",            # Root is default.
            #passwd="pass1",        # Password. Not using one right now.
        )
        m_connected = True
    except Exception as e:
        # Connection failed, return false.
        log.debug("database.initialize(): Can't access Database")
        m_connected = False
        return m_connected
        
    # Prove you are connected
    log.debug("database.initialize(): Proof of Connection: " + str(m_mydb))

    # Get the cursor
    m_cursor = m_mydb.cursor()
    
    
def isConnected():
    return m_connected


# Commit database changes
def commitDatabase():
    m_mydb.commit()



# Inserts a new entry into the 'songs' table.
# NOTES
# Doesn't yet account for duplicates
def insertNew(artist, track):
    log.debug("database.insertNew():")
    log.debug(f"database.insertNew():{artist},{track}")
    
    # Construct Command -- Insert artist and track into table 'songs'
    command = f"""
    USE lyrical_player_db;

    INSERT INTO songs (artist,track) 
    VALUES ("{artist}","{track}");
    """

    # Execute Command
    run_SQL(command)



# Gets the songID of the given artist and song.
# If the songID doesn't exist, it will create the
# songID and return that ID.
def getSongID(artist, song):
    
    # Will only run loop twice, to avoid a
    # forever-loop in case of error.
    i = 0
    while(i < 2):
        # Get songID. If NullType returned in SQL, 
        # string 'null' returned to python.
        # If null, will call insertNew() then run
        # code again. Else, return songID
        command = f"""
        USE lyrical_player_db;
        SELECT
          COALESCE(
            (
              SELECT
                songID
              FROM
                songs
              WHERE
                artist = "{artist}"
                AND track = "{song}"
            ),
            'null'
          );
        """
        run_SQL(command)
        
        songID = getCursorReturn()
        if(songID == 'null'):
            log.debug("database.getSongID(): songID was null")
            insertNew(artist,song)
            i = i + 1
        else:
            log.debug("database.getSongID(): " + str(songID))
            return songID
    
    # Throw an exception if null happens twice. Shouldn't happen, but just in case.
    raise Exception('Unspecified error. It seems songID returned a null value on both attempts.')



# Gets the artist and song of the given songID
# If the artist and song doesn't match a songID, it will return null
def getArtistAndSong(songID):
    command = f"""
    USE lyrical_player_db;
    
    SELECT
      COALESCE(
        (
          SELECT
            artist
          FROM
            songs
          WHERE
            songID = "{songID}"
        ),
        'null'
      );
    """
    run_SQL(command)
    str_artist = getCursorReturn()
    
    command = f"""
    USE lyrical_player_db;
    
    SELECT
      COALESCE(
        (
          SELECT
            track
          FROM
            songs
          WHERE
            songID = "{songID}"
        ),
        'null'
      );
    """
    run_SQL(command)
    str_song = getCursorReturn()
    
    return str_artist, str_song
 
 
# Returns the user query count for the given songID
def getUserQuery(songID):
    command = f"""
    USE lyrical_player_db;
    SELECT
      user_queries
    FROM
      songs
    WHERE
      songID = {songID}
    """
    run_SQL(command)
    
    ret_count = getCursorReturn()
    
    return ret_count
 
 
 
# Get the most searched songIDs
# Gets up to int_count songIDs
def getTopUserQuery(int_count):
    command = f"""
    USE lyrical_player_db;
    SELECT
      songID
    FROM
      songs
    ORDER BY
      user_queries DESC
    LIMIT
      {int_count};
    """
    run_SQL(command)
    
    arr_songID = []
    
    for x in range(int_count):
        ret_songID = getCursorReturn()
        log.debug(f"database.getTopUserQuery(): songID got: {ret_songID}")
        arr_songID.append(ret_songID)
    
    
    while(arr_songID.count('null') > 0):
        arr_songID.remove('null')
    
    return arr_songID
 
 
 
# Return user query count
def countUserQuery(songID):
    log.debug("database.countUserQuery():")
    int_count = getUserQuery(songID)
    int_count += 1
    log.debug(f"database.countUserQuery(): int_count: {int_count}")
    command = f"""
    USE lyrical_player_db;
    UPDATE
      songs
    SET
      user_queries = {int_count}
    WHERE
      songID = {songID};
    """
    run_SQL(command)
 
 
 
 
 
# Return user query count
def getUserQuery(songID):
    command = f"""
    USE lyrical_player_db;
    
    SELECT
      COALESCE(
        (
          SELECT
            user_queries
          FROM
            songs
          WHERE
            songID = {songID}
        ),
        'null'
      );
    """    
    run_SQL(command)
    
    query_return = getCursorReturn()
    
    if(query_return == 'null'):
        return -1
    return int(query_return)
    
    





# Get spotify embed URL
def getSpotifyEmbedURL(songID):
    command = f"""
    USE lyrical_player_db;
    SELECT
      COALESCE(
        (
          SELECT
            spotify_url
          FROM
            spotify_urls
            JOIN songs ON spotify_urls.songID = songs.songID
          WHERE
            songs.songID = {songID}
        ),
        'null'
      );
    """
    run_SQL(command)
    
    str_url = str(getCursorReturn())
    return str_url
 
 

# Set spotify embed URL
def setSpotifyEmbedURL(songID, spt_url):
    command = f"""
    USE lyrical_player_db;
    INSERT INTO
      spotify_urls (songId, spotify_url)
    VALUES
      ({songID}, "{spt_url}") ON DUPLICATE KEY
    UPDATE
      spotify_url = "{spt_url}";
    """
    run_SQL(command)
 
 
 
 
 
 
# Returns a URL for an image 
# for the associated songID
def getImageURL(songID):
    command = f"""
    USE lyrical_player_db;
    SELECT
      COALESCE(
        (
          SELECT
            image_url
          FROM
            image_urls
            JOIN songs ON image_urls.songID = songs.songID
          WHERE
            songs.songID = {songID}
        ),
        'null'
      );
    """
    run_SQL(command)
    
    str_url = str(getCursorReturn())
    return str_url
 
 

def setImageURL(songID, img_url):
    
    command = f"""
    USE lyrical_player_db;
    INSERT INTO
      image_urls (songId, image_url)
    VALUES
      ({songID}, "{img_url}") ON DUPLICATE KEY
    UPDATE
      image_url = "{img_url}";
    """
    run_SQL(command)
    
    
 
 
 
 
 
 
 
 
 


# Returns the lyrics for the given songID.
def getLyrics(songID):
    # Get Lyrics
    command = f"""
    SELECT
      COALESCE(
        (
          SELECT
            lyrics.lyrics
          FROM
            lyrics
            JOIN songs ON lyrics.songID = songs.songID
          WHERE
            songs.songID = {songID}
        ),
        'null'
      );
    """
    run_SQL(command)
    str_lyrics = getCursorReturn()
    
    # Return lyrics.
    return str_lyrics
   
   
   
# Sets lyrics into the database at the given
# songID. Shouldn't need any exception cases.
# NOTES
# Not sure if I did ON DUPLICATE KEY UPDATE properly. Seems to have worked so far.
def setLyrics(songID, lyrics):
    # Construct Command -- Insert lyrics into 'lyrics' table with given songID
    command = f"""
    USE lyrical_player_db;
    INSERT INTO
      lyrics (songId, lyrics)
    VALUES
      ({songID}, "{lyrics}") ON DUPLICATE KEY
    UPDATE
      lyrics = "{lyrics}";
    """
    
    # Execute Command
    run_SQL(command)   
   



# Sets lyrics into the database at the given
# songID. Shouldn't need any exception cases.
# NOTES
# Not sure if I did ON DUPLICATE KEY UPDATE properly. Seems to have worked so far.
def setSpotifyTopList(int_rank, int_songID, int_time):
    # Construct Command -- Insert lyrics into 'lyrics' table with given songID
    command = f"""
    USE lyrical_player_db;
    INSERT INTO
      spotifyTopList (rank, songID, updateTime)
    VALUES
      ({int_rank}, {int_songID}, {int_time}) ON DUPLICATE KEY
    UPDATE
      songID = {int_songID},
      updateTime = {int_time};
    """
    
    # Execute Command
    run_SQL(command)



# Returns the songID for the Spofity song at rank int_rank
def getSpotifyRankID(int_rank):
    # Get from rank
    command = f"""
    SELECT
      COALESCE(
        (
          SELECT
            spotifyTopList.songID
          FROM
            spotifyTopList
          WHERE
            spotifyTopList.rank = {int_rank}
        ),
        'null'
      );
    """
    run_SQL(command)
    str_songID = getCursorReturn()
    
    # if null, return "null"
    return str_songID
    
    
    
def getSpotifyRankTime(int_songID):
    # Get time from ID
    command = f"""
    SELECT
      COALESCE(
        (
          SELECT
            spotifyTopList.updateTime
          FROM
            spotifyTopList
          WHERE
            spotifyTopList.songID = {int_songID}
        ),
        'null'
      );
    """
    run_SQL(command)
    str_updateTime = getCursorReturn()
    
    # If null, return "null"
    return str_updateTime




# Show the provided table
def showTable(table):
    log.debug("database.show(): Showing Table %s" % (table))
    m_cursor.execute("USE lyrical_player_db")       # Use the database
    m_cursor.execute("SELECT * FROM %s" % (table))  # Select all from table
    for x in m_cursor:
        print(x)



# Returns what is in the cursor as a string.
def getCursorReturn():
    try:
        return str(m_cursor.fetchone()[0])
    except:
        return 'null'

# Easy SQL execute
# Create a single string with all your ocmmends, send it
# to this function to execute all of them.
# WARNING will not work if a ';' is used as anything
# other than a statement termination
def run_SQL(command):
    global m_connected
    
    log.debug("database.run_SQL():")
    if(m_connected):
        commands = command.split(";")
        for e in commands:
            e = e+";"
            if(e.strip() != ";"):
                m_cursor.execute(e) #This executes a line of code in SQL
    else:
        log.debug("database.run_SQL(): Not connected to database, can't run SQL code.")

