import streamlit as st

st.sidebar.title("Menu")

st.sidebar.slider("Slider 1", 0, 100, 50)
st.sidebar.slider("Slider 2", 0, 100, 50)

st.sidebar.selectbox(
    "Choose an option",
    ["Option 1", "Option 2", "Option 3"]
)

st.title("Hello, Streamlit")

st.write("Web-app")