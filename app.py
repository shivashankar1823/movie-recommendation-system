import pickle
import streamlit as st
import pandas as pd
import os
import gdown
import requests

# =========================
# DOWNLOAD similarity.pkl (SAFE VERSION)
# =========================

FILE_ID = "1NKP9eNUm9W-hoYpbEspYdNG16_Pu3hNV"

def download_similarity():
    url = f"https://drive.google.com/uc?id={FILE_ID}"
    gdown.download(url, "similarity.pkl", quiet=False)

# Remove corrupted file (IMPORTANT)
if os.path.exists("similarity.pkl"):
    if os.path.getsize("similarity.pkl") < 1000000:  # <1MB → wrong file
        os.remove("similarity.pkl")

# Download if not present
if not os.path.exists("similarity.pkl"):
    with st.spinner("Downloading similarity.pkl... (first time only)"):
        download_similarity()


# =========================
# FETCH POSTER FUNCTION
# =========================

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=97fe2b95036aff6e1dd40cbcd3e0689b&language=en-US"
    
    try:
        data = requests.get(url)
        data.raise_for_status()
        data = data.json()
        
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
    
    return "https://placehold.co/500x750/333/FFFFFF?text=No+Poster"


# =========================
# RECOMMEND FUNCTION
# =========================

def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Movie not found. Please select another.")
        return [], [], [], []
        
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    names, posters, years, ratings = [], [], [], []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id

        names.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))
        years.append(movies.iloc[i[0]].year)
        ratings.append(movies.iloc[i[0]].vote_average)

    return names, posters, years, ratings


# =========================
# STREAMLIT UI
# =========================

st.set_page_config(layout="wide")
st.header("🎬 Movie Recommender System Using Machine Learning")


# =========================
# LOAD FILES SAFELY
# =========================

try:
    # Load movie dictionary
    movies_dict = pickle.load(open('artifacts/movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)

    # Load similarity matrix
    similarity = pickle.load(open('similarity.pkl', 'rb'))

except FileNotFoundError as e:
    st.error("❌ Required file not found")
    st.text(str(e))
    st.stop()

except Exception as e:
    st.error("❌ Error loading model files")
    st.text(str(e))
    st.stop()


# =========================
# UI INTERACTION
# =========================

movie_list = movies['title'].values

selected_movie = st.selectbox(
    "Type or select a movie",
    movie_list
)

if st.button("Show Recommendation"):
    with st.spinner("Finding recommendations..."):
        names, posters, years, ratings = recommend(selected_movie)

    if names:
        cols = st.columns(5)

        for i, col in enumerate(cols):
            with col:
                st.text(names[i])
                st.image(posters[i])

                year = years[i]
                if pd.notna(year):
                    st.caption(f"Year: {int(year)}")
                else:
                    st.caption("Year: N/A")

                st.caption(f"Rating: {ratings[i]:.1f} ⭐")
