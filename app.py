import pickle
import streamlit as st
import requests
import pandas as pd
import os

FILE_ID = "1NKP9eNUm9W-hoYpbEspYdNG16_Pu3hNV"
URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

def download_file():
    response = requests.get(URL, stream=True)
    
    if response.status_code == 200:
        with open("similarity.pkl", "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    else:
        st.error("❌ Failed to download similarity.pkl")
        st.stop()

if not os.path.exists("similarity.pkl"):
    with st.spinner("Downloading similarity.pkl... (first time only)"):
        download_file()

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


st.set_page_config(layout="wide")
st.header("🎬 Movie Recommender System Using Machine Learning")


try:
    movies_dict = pickle.load(open('artifacts/movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)

    similarity = pickle.load(open('similarity.pkl', 'rb'))

except FileNotFoundError:
    st.error("❌ Required files not found. Check your repo.")
    st.stop()

except Exception as e:
    st.error("❌ Error loading model files")
    st.text(str(e))
    st.stop()


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
