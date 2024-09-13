import streamlit as st
from streamlit_option_menu import option_menu

# Configure the page
st.set_page_config(page_title="Homework Manager", layout="wide")

# Sidebar navigation menu
with st.sidebar:
    selected_page = option_menu(
        menu_title="HW Manager",
        options=["First Homework", "Second Homework"],
        icons=['book', 'beaker'],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5rem 1rem", "background-color": "#f0f2f6"},
            "icon": {"color": "orange", "font-size": "1.5rem"},
            "nav-link": {"font-size": "1.2rem", "text-align": "left", "margin": "0.5rem 1rem", "color": "#333"},
            "nav-link-selected": {"background-color": "#e9ecef"},
        }
    )

# Page content based on selected menu item
if selected_page == "First Homework":
    st.title("Homework 1")
    # Execute the content of hw1.py
    exec(open("hw1.py").read())

elif selected_page == "Second Homework":
    st.title("Homework 2")
    # Execute the content of hw2.py
    exec(open("hw2.py").read())
