import streamlit as st 
from spotify_auth import spotify_auth
from user_data import * # display_user_data, get_playlists, get_playlist_tracks
from lyrics import * # match_lyrics, clean_lyrics, summarize_lyrics, predict_sentiment
from recommend import recommend

# Page title
st.set_page_config(page_title="SpotiMine")
st.title("SpotiMine - Playlist Recommender")

# Spotify Authentication
if "spotify_client" not in st.session_state:
    st.session_state["spotify_client"] = None

if st.session_state["spotify_client"] is None:
    login = st.empty()
    with login.container():
        st.info("Log in to Spotify to get started")
        auth_button = st.button("Login with Spotify")
        
    if auth_button:
        sp = spotify_auth()
        if sp:
            st.session_state["spotify_client"] = sp
            current_user = display_user_data(sp)
            login.empty()
            # User information
            st.success(f"Logged in as {current_user['display_name']}")
            st.image(current_user['images'][0]['url'], width=50)
        else:
            st.error("Login failed.")

if st.session_state["spotify_client"]:
    sp = st.session_state["spotify_client"]
    # Input current music mood
    st.header("Current Mood")
    user_mood = st.text_input("What's the occasion?", "falling in love with the guy across the room")

    # Get user's playlists
    user_playlists = get_playlists(sp)
    playlist_names = [playlist['name'] for playlist in user_playlists]

    # Display user's playlists for selection
    st.header("Playlists")
    selected_playlist = st.selectbox("Choose a playlist", playlist_names, index = None)
    # Playlist description
    playlist_description = ''.join(p['description'] for p in user_playlists if p['name'] == selected_playlist)
    st.write(playlist_description)
    
    
    # Display playlist tracks
    playlist_id = ''.join(p['id'] for p in user_playlists if p['name'] == selected_playlist)
    if playlist_id:
        tracks = get_playlist_tracks(sp, playlist_id)
        st.write(pd.DataFrame(tracks).sample(50))
        
        # Match lyrics
        with st.spinner("Matching lyrics..."):
            lyrics_df = match_lyrics(pd.DataFrame(tracks))
            lyrics_df = clean_lyrics(lyrics_df, 'lyrics')
        st.write("Lyrics found!")
        
        # Sentiment Analysis
        with st.spinner("Summarizing your playlist..."):
            summaries = []
            for lyrics in lyrics_df['lyrics']:
                summaries.append(summarize_lyrics(lyrics))
            lyrics_df['summary'] = summaries
            lyrics_sample = lyrics_df.sample(6)['summary']
        
        user_mood = user_mood + "." + playlist_description + ".".join(lyrics_sample) 
            
        st.header("Summarization completed!")
        st.write(summarize_lyrics(user_mood))
        
        st.header("Here's your playlist")
        st.write(recommend(sp, user_mood))
        
            