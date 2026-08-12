import streamlit as st

st.title("Hello, World!")
st.write("This is a simple Streamlit app.")

name = st.text_input("What's your name?")
if name:
    st.write(f"Nice to meet you, {name}!")

if st.button("Click me"):
    st.balloons()
