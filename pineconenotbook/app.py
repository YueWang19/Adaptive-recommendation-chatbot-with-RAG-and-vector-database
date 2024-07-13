import streamlit as st
from ragchatbot import get_answers


st.title("Wedding music recommendation Chatbot")

query = st.text_input("Enter your question:")

if query:
    answer = get_answers(query)
    st.write(f"**Answer:** {answer}")


