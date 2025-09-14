import streamlit as st
import pickle
import pandas as pd
import requests

# Background Video Configuration
st.markdown(
    """
    <style>
    .stApp {
        background: transparent;
        border: 3px solid purple;
    }

    #video-background {
        position: fixed;
        top: 0;
        left: 0;
        min-width: 100vw;
        min-height: 100vh;
        width: auto;
        height: auto;
        z-index: -1;
        object-fit: cover;
        opacity: 0.3;
        filter: brightness(0.7);
    }

    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(5px);
        color: purple;
        font-weight : 600;
    }

    .stButton > button {
        background-color: rgba(0, 123, 255, 0.9) !important;
        backdrop-filter: blur(5px);
        
    }

    h1 {
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        color: white !important;
    }

    h3 {
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        color: white !important;
    }

    .top-right-text {
        position: fixed;
        top: 60px;
        right: 10px;
        text-align: right;
        font-size: 14px;
        color: pink;
        font-family: monospace;
        z-index: 100;
    }
    </style>

    <video autoplay loop muted playsinline id="video-background">
        <source src="https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4" type="video/mp4">
        <source src="https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4" type="video/mp4">
    </video>

    <div class="top-right-text">
    ~By Harshita Goyal<br>
    Btech CSE<br>
    2023078035
    </div>
    """,
    unsafe_allow_html=True
)

OMDB_API_KEY = "24d5efc4"


@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity


def fetch_poster(title):
    try:
        params = { "t":title, "apikey":OMDB_API_KEY}
        response = requests.get("http://www.omdbapi.com/", params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_url = data.get("Poster")
        if poster_url and poster_url!="N/A": return poster_url

    except Exception:
        pass  # Ignore all poster fetch errors
    return None


movies, similarity = load_data()


def recommend(movie):
    if movie not in set(movies['title']):
        return []
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]
    recommendations = []
    for i in movies_list:
        title = movies.iloc[i[0]].title
        poster_url = fetch_poster(title)
        recommendations.append((title, poster_url))
    return recommendations


st.title('Flicksy')

option = st.selectbox(
    'Select a movie:',
    movies['title'].values
)

if st.button('Recommend'):
    recommendations = recommend(option)
    if not recommendations:
        st.write("No recommendations found. Try another movie or check your network.")
    else:
        st.subheader("Recommended Movies:")
        cols = st.columns(5)
        for idx, (title, poster_url) in enumerate(recommendations):
            with cols[idx]:
                if poster_url:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.write("No poster")
                st.markdown(f"{title}")
