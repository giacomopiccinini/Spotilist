import streamlit as st
import spotipy
import pandas as pd

from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from Code.Class.Search import Search


###### APP INFO AND LAYOUT ######

app_name = "Spotilist"

# Set general settings for app
st.set_page_config(
    page_title=f"{app_name}",
    initial_sidebar_state="expanded",
    menu_items={
        "About": f"# {app_name} \n Designed and engineered by Giacomo Piccinini"
    },
)

st.title("Spotilist")

###### DESCRIPTION ######

st.markdown("## Introduction")
st.markdown(
    "A direct way to be featured in a Spotify playlist is to contact the curator directly. If you are not yet famous, you may want to restrict yourself to playlists that:"
)
st.markdown("- Cover your genre;")
st.markdown("- Include emerging artists.")
st.markdown(
    "The purpose of this app is to find, amongst all the Spotify playlists, those that meet your search criteria (i.e., your query)."
)

###### HOW IT WORKS ######

st.markdown("## How it works")
st.markdown(
    "The app works like this: you are asked to enter a query for your search. This should contain a description of the type of playlist you are looking for. For example, '*modern progressive rock*'."
)
st.markdown(
    "In addition, you will have to enter the total number of playlists to be displayed and the curators to be excluded."
)
st.markdown(
    "This is to avoid considering curators who are too famous and whom you cannot reasonably address."
)
st.markdown(
    "Finally, you might want to exclude playlists whose *least famous* artist has more than a certain number of followers. To do so, adjust the the 'Maximum number of followers' parameter."
)

###### IMPLEMENTATION ######

st.markdown("## Search")

# Load variables from .env file and export them
load_dotenv()

# Initialize Spotify Credential manager
authentication = SpotifyClientCredentials()

# Initialize Spotify client
spotify = spotipy.Spotify(auth_manager=authentication)

# Search query
query = st.text_input(
    label="Search query", placeholder="Example: modern progressive rock"
)

# Number of results
n_results = st.number_input(
    label="Number of playlists", min_value=1, max_value=100, value=10
)

# Curators to exclude
curators_to_exclude = st.text_input(
    "Curators to exclude (separate with comma)",
    placeholder="Spotify, Century Media Records, The Sounds of Spotify",
)

# Cutoff to be applied on followers
followers_cutoff = st.number_input(label="Maximum number of followers", value=100)

# Pre-process curators
curators_to_exclude = curators_to_exclude.split(",")
curators_to_exclude = [curator.lstrip() for curator in curators_to_exclude]

# Initialise search class
search = Search(n_results, spotify, query, curators_to_exclude, followers_cutoff)

# Button for actually running search
click = st.button(label="Run search", on_click=search.search)

if click:

    ###### RESULTS ######

    st.markdown("## Results")

    st.dataframe(
        st.session_state["search"].df[["PlaylistName", "Followers", "CuratorName"]]
    )
