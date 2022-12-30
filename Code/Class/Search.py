import pandas as pd
import streamlit as st


class Search:
    def __init__(
        self, n_results, spotify, query, curators_to_exclude, followers_cutoff
    ):

        # Initialise dataframe
        self.df = pd.DataFrame(
            columns=[
                "PlaylistName",
                "Followers",
                "PlaylistID",
                "CuratorName",
                "CuratorID",
                "CuratorFollowers",
            ]
        )

        # Set variables
        self.n_results = n_results
        self.spotify = spotify
        self.query = query
        self.curators_to_exclude = curators_to_exclude
        self.followers_cutoff = followers_cutoff

    def search(self):

        # Counter of acceptable playlist
        self.playlist_counter = 0

        # Counter of search iterations
        self.iteration_counter = 0
        
        completion_bar = st.progress(0)

        while self.playlist_counter < self.n_results:
            
            completion_bar.progress(self.playlist_counter/self.n_results)

            # Search
            self.single_search()
            
        completion_bar.progress(1.0)

        # Restrict to desired number of results
        self.df = (
            self.df.sort_values(by=["Followers"]).head(self.n_results).reset_index()
        )

        st.session_state["search"] = self

    def single_search(self):

        # Fetch results from Spotify
        results = self.spotify.search(
            q=self.query, limit=20, offset=self.iteration_counter * 20, type="playlist"
        )

        # Retrieve actual playlists
        playlists = results["playlists"]["items"]

        # Get playlists names and ids
        playlist_names = [playlist["name"] for playlist in playlists]
        playlist_ids = [playlist["id"] for playlist in playlists]

        # Get curators names and ids
        curator_names = [playlist["owner"]["display_name"] for playlist in playlists]
        curator_ids = [playlist["owner"]["id"] for playlist in playlists]

        # Create dataframe
        new_df = pd.DataFrame(
            data={
                "PlaylistName": playlist_names,
                "PlaylistID": playlist_ids,
                "CuratorName": curator_names,
                "CuratorID": curator_ids,
            }
        )

        # Exclude famous curators
        for curator in self.curators_to_exclude:
            new_df = new_df[new_df["CuratorName"] != curator]

        # Initialise minima counting
        minima = []

        # Routine to check if playlist contains non-famous artists
        for playlist_id in new_df["PlaylistID"]:

            # Get tracks
            tracks = self.spotify.playlist_tracks(playlist_id=playlist_id)["items"]

            # Sort by popularity
            tracks.sort(key=lambda track: track["track"]["popularity"])

            # Cutoff to first tracks (those less popular)
            tracks = tracks[:5]

            # Get corresponding artist id (use "0" to only get the first artist, if multiple)
            artist_ids = [track["track"]["artists"][0]["id"] for track in tracks]

            # Remove artists with None id
            artist_ids = list(filter(lambda item: item is not None, artist_ids))

            # Get artists data
            artists_data = self.spotify.artists(artist_ids)["artists"]

            # Get followers of each artist
            artist_followers = [artist["followers"]["total"] for artist in artists_data]

            # Calculate minimum number of followers
            minimum = min(artist_followers)

            # Append to minima
            minima.append(minimum)

        # Add followers column
        new_df["Followers"] = minima

        # Filter out artists with more than required followers
        new_df.query("Followers < @self.followers_cutoff", inplace=True)

        # Sort by followers
        new_df.sort_values(by=["Followers"], inplace=True)

        # Find followers of the curator
        curator_followers = [
            self.spotify.user(curator_id)["followers"]["total"]
            for curator_id in new_df["CuratorID"]
        ]

        # Write to df
        new_df["CuratorFollowers"] = curator_followers

        # Concatenate
        self.df = pd.concat([self.df, new_df], ignore_index=True)

        # Increment counter
        self.iteration_counter += 1

        # Increment playlist counter
        self.playlist_counter += len(new_df)
