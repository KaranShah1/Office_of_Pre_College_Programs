import streamlit as st
from streamlit_option_menu import option_menu

# Set up a sidebar or navigation for different pages
st.set_page_config(page_title="Multi-Page App", layout="wide")

# Define navigation using a simple option menu
with st.sidebar:
    selected_page = option_menu(
        "Pre College Bot",
        ["Test Bot", "Pre-College Bot", "Smart Pre-College Bot", "SRC Pre-College Bot", "Final Testing Bot"],
        icons=['beaker', 'beaker', 'beaker', 'beaker', 'beaker'],
        menu_icon="cast", 
        default_index=0,
    )
    
st.set_page_config(page_title="Interactive Travel Guide Chatbot", page_icon="🌎", layout="wide")
    

# Load the appropriate page based on the user's selection
if selected_page == "Test Bot":
    st.title("SU Office of Pre-College Programs")
    # Execute the cps1.py code
    exec(open("cps1.py").read())  # This will run the content of cps1.py

elif selected_page == "Pre-College Bot":
    st.title("Syracuse University Office of Pre-College Programs")
    # Execute the hw2.py code
    exec(open("cps2.py").read())  # This will run the content of cps2.py

elif selected_page == "Smart Pre-College Bot":
    st.title("Syracuse University Office of Pre-College Programs")
    # Execute the hw2.py code
    exec(open("cps3.py").read())  # This will run the content of cps3.py

elif selected_page == "SRC Pre-College Bot":
    st.title("Syracuse University Office of Pre-College Programs")
    # Execute the cps4.py code
    exec(open("cps4.py").read())  # This will run the content of cps4.py

elif selected_page == "Final Testing Bot":
    st.title("Syracuse University Office of Pre-College Programs")
    # Execute the cps5.py code
    exec(open("cps5.py").read())  # This will run the content of cps5.py



