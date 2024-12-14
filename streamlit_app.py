import streamlit as st
from streamlit_option_menu import option_menu

# Set up the main page configuration
st.set_page_config(page_title="Interactive Travel Guide Chatbot", page_icon="🌎", layout="wide")

# Define navigation with a single active page
with st.sidebar:
    selected_page = option_menu(
        "Pre College Bot",
        ["Final Testing Bot"],  # Only one option
        icons=['beaker'],  # Single icon
        menu_icon="cast",
        default_index=0,  # Default to this page
    )

# Only the "Final Testing Bot" is active
if selected_page == "Final Testing Bot":
    st.title("Syracuse University Office of Pre-College Programs")
    # Execute the cps5.py code
    exec(open("cps5.py").read())  # This will run the content of cps5.py

# Commented out all other pages
# elif selected_page == "Test Bot":
#     st.title("SU Office of Pre-College Programs")
#     exec(open("cps1.py").read())  # Run cps1.py

# elif selected_page == "Pre-College Bot":
#     st.title("Syracuse University Office of Pre-College Programs")
#     exec(open("cps2.py").read())  # Run cps2.py

# elif selected_page == "Smart Pre-College Bot":
#     st.title("Syracuse University Office of Pre-College Programs")
#     exec(open("cps3.py").read())  # Run cps3.py

# elif selected_page == "SRC Pre-College Bot":
#     st.title("Syracuse University Office of Pre-College Programs")
#     exec(open("cps4.py").read())  # Run cps4.py
