# Lyrical-Player-Website
CAPSTONE Final Project
![Image of Website](https://i.imgur.com/1NaFh6K.png)

## Description
This project was the final project for my Computing and Informatics degree. I worked on this in a team of me and two other classmates.

The project definition was vague in terms of content: pick a theme, create a website around that theme. Each person in the group will use at least one web API to gather data from the Internet, and save that to a SQL database. Then, we will recall that data to display on our website.
We later added a 'Top List' using the Spotify API — We pulled songs from Spotify's 'Today's Top Hits' playlist to display as quick-links to popular songs, and we would update that list every 24 hours or so. We also added the ability for the user to add lyrics to a song if no lyrics were found, which were then stored into the database to be called up when that song was next searched.

For our group, we chose a theme of 'music', with the intention of creating a lyrical database website. One API would retrieve lyrics, one would retrieve images, and the last would play the searched song. We decided to each use Python to utilize the APIs because 1) we were all familiar with the languages, 2) Python is a very accessible language that has many libraries for getting things done quickly and easily. 
## Work
#### The Modules
We used a modular structure to the project. We would each write our APIs that would do their own thing, then use another module to communicate with each API to accomplish the task. `flask_host.py` hosted the website using the Flask library, and also handled communication between the other APIs: `spotify_api.py`, `lyrics_api.py`, `images_api.py`, and `database.py`. 
#### Lyrics API
I did the lyrics, which I accomplished by using `azlyrics.com`. This was accomplished in a slighly roundabout fashion, but it worked; I loaded in the html page for the searched song using urllib.request and BeautifulSoup, collected the content of the page (which would be the lyrics), then cleaned up the HTML tags to work with Python strings properly. 
#### Flask_Host and Database
As for the other modules, we used Google Images to retrieve images, and Spotify to play music using HTML embeds. We also have a fourth module called `database.py` that handled communication with the SQL server.

As I ended up having the easiest API to implement, I had extra time to work on the `flask_hosy.py` and `database.py` modules. I wound up writing much of the code for those two modules myself. I also did all the HTML and CSS code and design for the website itself.
#### SQL Database
I unfortunately have lost the SQL database I'd set up for this project, and so I don't have that to add. Perhaps I will recreate it and add it to the repository if I have time later. Going from memory, it was set up something like this:
```
Table: songs
columns: songid[PRIMARY, INT], artist[CHAR(128)], track[CHAR(128)]
```
```
Table: lyrical_player_db
columns: songid[PRIMARY, INT], lyrics[CHAR(9000)]
```
```
Table: spotify_urls
columns: songid[PRIMARY, INT], spotify_url[CHAR(128)]
```
```
Table: image_urls
columns: songid[PRIMARY, INT], image_url[CHAR(128)]
```
```
Table: spotifyTopList
columns: rank[INT], songID[INT], updateTime[INT]
```



Our original project write-up:
```Our project’s original theme was around music. The concept was that a user can search for a song by title and artist. Our website would play the song with a spotify embed, provide lyrics for the song, and call up some artwork related to that song, artist, or album. The website would keep track of the number of queries for any particular song and provide a top-10 list of the most popular searches. Josh worked on the Spotify API, Tyler used the GoogleCustomSearch API, and Lucas used the Beautiful Soup API to access the AZLyrics website and retrieve lyrics. The plan from the beginning was to implement all our code in the same language: Python.

This project was the first time any of us had utilized a database using python, as well as the first time using Flask and Jinja to mediate between python and a website. For the most part, the initial set-up was fairly easy. Once we had our individual APIs connecting and retrieving data, we each reorganized our code to operate in a modular, functional manner. This made the transition easy and seamless, allowing us to create one master file which could utilize each API from its own module, as opposed to putting all the code into a single script file.

We ran into an initial roadblock while setting up Flask in Lucas’ installation where he was having difficulty importing Flask. After some head-scratching and google searching, we determined it was because he initially named his file flask.py. This caused python to attempt to import flask.py from within the script itself, causing an ImportError with the message “cannot import name 'Flask' from partially initialized module 'flask' (most likely due to a circular import).” The fix was as simple as renaming the file to something else, in this case flask_host.py.
Additionally, we ran into overrun issues with our database. Our project inserts entire song lyrics into the DB, and our initial size of varchar(512) was inadequate for this. We searched for the lyrically longest song — which is Eminem’s Rap God at 8057 characters — and changed the size of the table to account for a varchar(9000). This should account for most any song.
While setting up Spotipy, Josh had a lot of errors with authentication and session tokens, even when following the examples in the documentation. The keys were not storing and importing correctly from the Spoitpy library. This was solved by manually declaring the key values within the code.  
The Apache server running on localhost interfered with the Spotify user authentication process, since it would redirect to the Xampp home screen instead of the expected Spotify auth screen. We ended up not needing this feature anyway (perhaps we would add in future builds), but it was still something Josh spent a good amount of time on trying to fix and implement it into Flask.

An additional problem later came up in testing when certain lyrics caused an error in MySQL when we tried to store them in the database. It was discovered that this was due to certain characters causing an error when trying to be used in MySQL, as they were special characters that were reserved for special uses.  To fix this, we had to add escape characters to the string in Python before running them through MySQL in order to conform to MySQL syntax.
In terms of what we wish we could have done, a big thing would be to add user accounts.  With these, we could store what a user’s favorite songs were, allow them to create personal playlists that would autoplay the songs in sequence, count the number of times a user has listened to a song, and the last time a user had searched for a specific song.  Outside of the autoplay, we know all of these implementations should be possible, however they would take more time then we have available this semester.  Another thing we would have liked to add would have been a listing for other songs by the current artist.  Since we already had the current artist stored, this could easily be done with a little more time.  Finally, while we currently have the top songs listed, this is just top songs in general.  Giving the user the option of searching for top songs by genre would be a way to take it a step further.```
