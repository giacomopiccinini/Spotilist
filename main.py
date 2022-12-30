import spotipy
import pandas as pd

from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

# Load variables from .env file and export them
load_dotenv()

# Initialize Spotify Credential manager
authentication = SpotifyClientCredentials()

# Initialize Spotify client
spotify = spotipy.Spotify(auth_manager=authentication)

# Search query
query = input("Search Query:\n")

# Fetch results from Spotify
results = spotify.search(q=query, limit=50, type="playlist")

# Retrieve actual playlists
playlists = results["playlists"]["items"]

# Get playlists names and ids
playlist_names = [playlist["name"] for playlist in playlists]
playlist_ids = [playlist["id"] for playlist in playlists]

# Get curators names and ids
curator_names = [playlist["owner"]["display_name"] for playlist in playlists]
curator_ids = [playlist["owner"]["id"] for playlist in playlists]

# Create dataframe
df = pd.DataFrame(
    data={
        "PlaylistName": playlist_names,
        "PlaylistID": playlist_ids,
        "CuratorName": curator_names,
        "CuratorID": curator_ids,
    }
)

# Curators to exclude
curators_to_exclude = ["Spotify", "Century Media Records", "The Sounds of Spotify"]

# Exclude famous curators
for curator in curators_to_exclude:
    df = df[df["CuratorName"] != curator]

# Initialise minima counting
minima = []

# Routine to check if playlist contains non-famous artists
for playlist_id in df["PlaylistID"]:

    # Get tracks
    tracks = spotify.playlist_tracks(playlist_id=playlist_id)["items"]

    # Sort by popularity
    tracks.sort(key=lambda track: track["track"]["popularity"])

    # Cutoff to first tracks (those less popular)
    tracks = tracks[:5]

    # Get corresponding artist id (use "0" to only get the first artist, if multiple)
    artist_ids = [track["track"]["artists"][0]["id"] for track in tracks]

    # Get artists data
    artists_data = spotify.artists(artist_ids)["artists"]

    # Get followers of each artist
    artist_followers = [artist["followers"]["total"] for artist in artists_data]

    # Calculate minimum number of followers
    minimum = min(artist_followers)

    # Append to minima
    minima.append(minimum)

# Add followers column
df["Followers"] = minima

# Sort by followers
df.sort_values(by=["Followers"], inplace=True)

