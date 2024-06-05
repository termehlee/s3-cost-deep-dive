import streamlit as st
import utils.pricing as pricing
import gettext
from st_pages import Page, show_pages, add_page_title, show_pages_from_config, Section

show_pages_from_config("s3_cost_sim/.streamlit/pages.toml")
add_page_title(add_icon=False,
               page_title="S3 Cost Simulation",
            page_icon="☁️",
               layout="wide",
               menu_items={
        'Get Help': 'mailto:tamelly@amazon.com',
        'About': "Property of Amazon"
    })

st.sidebar.success("Select a module above.")

if 'home_region' not in st.session_state:
    st.session_state['home_region'] = 'us-east-1'

st.markdown(
    """
    This app is an Amazon S3 workshop for deep diving into S3 costs. **👈 Select a demo from the sidebar** to see some examples of how Amazon S3 costing works!
    ### Want to learn more?
    - Check out [Amazon S3](https://aws.amazon.com/s3/)
    - Jump into our [pricing page](https://aws.amazon.com/s3/pricing/?nc=sn&loc=4)
    - Provide feedback to our developer - [Tamelly Lim](tamelly@amazon.com)
    """
)