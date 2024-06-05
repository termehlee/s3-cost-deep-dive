import streamlit as st
import utils.pricing as pricing
from st_pages import show_pages_from_config, add_indentation

add_indentation()


# st.set_page_config(page_title="Hybrid Cloud", page_icon="☁️", layout="wide")
st.title("Scenario #3: Data Lake")
st.sidebar.selectbox("Select a Region:", pricing.region_code, key='home_region')

form = st.form("input")
home_region = st.session_state['home_region']
