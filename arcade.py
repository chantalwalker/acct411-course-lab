"""Deploy this entrypoint to offer both games in ONE private Streamlit app."""
import streamlit as st

# Each page keeps its own source file. A single deployment serves both pages.
page = st.navigation([
    st.Page('gin_rummy/app.py', title='Velvet Gin', icon='♠', url_path='gin', default=True),
    st.Page('tetris/app.py', title='Tetris', icon='🧩', url_path='tetris'),
])
page.run()
