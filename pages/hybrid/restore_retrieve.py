import streamlit as st
import utils.pricing as pricing
import streamlit_shadcn_ui as ui
import utils.helper as helper
import math
import pandas as pd
import numpy as np
import plotly.express as px  # interactive charts
from st_pages import show_pages_from_config, add_indentation, add_page_title
import math


LARGEST_FILE_SIZE = helper.convert_storage_size(5, 'TB', 'MB')
MAX_REQUESTS = 10000

GET_REQUEST_COST = 'GET Request Cost per 1000 files'
RETRIEVAL_COST = 'Retrieval Cost per GB'
RETRIEVAL_REQUEST_COST = 'Retrieval Cost per 1000 Requests'
TOTAL_GET_REQUEST_COST = 'Total GET Request cost'
TOTAL_RETRIEVAL_COST = 'Total Data Retrieval cost'
TOTAL_RETRIEVAL_REQUEST_COST = 'Total Retrieval Requests cost'
TOTAL_COST = 'Total cost'
GLACIER_CLASSES = ['S3 Glacier Flexible Retrieval', 'S3 Glacier Deep Archive']

# @st.experimental_fragment
def retrieval_form():
    form = st.form('retrieval')
    with form:
        st.write("### Input the parameters for retrieval cost")
        size_col, unit_col = st.columns([3, 1])
        with size_col:
            st.number_input("Size of each file to be retrieved", value=1, key='size')
        with unit_col:
            st.selectbox("Unit", ["MB", "GB", "TB"], index=0, key='unit')
        st.number_input("Number of files for retrieval", min_value=1, value=1000, key='files_retrieval')
        st.multiselect("Target storage classes for comparision", list(pricing.s3_storage_classes_excl_int), key='selected_storage_class')
        retrieval_submitted = st.form_submit_button("Confirm")
    return retrieval_submitted

def validate_retrieval_input(total_size_MB):
    # Validate maximum file size
    if total_size_MB > LARGEST_FILE_SIZE:
        st.error("File size is too large. Maximum size for each file stored in Amazon S3 is 5 TB.")
        return False
    
    # Validate storage classes selected
    if not st.session_state.selected_storage_class: 
        st.error("Please select at least one storage class")
        return False
    
    return True

def get_retrieval_pricing():
    df = pd.DataFrame(columns=st.session_state.selected_storage_class, index=[GET_REQUEST_COST, RETRIEVAL_COST, RETRIEVAL_REQUEST_COST])
    for storage_class in st.session_state.selected_storage_class:
        storage_class_code =  pricing.s3_storage_classes[storage_class]
        get_cost = pricing.get_s3_get_cost(storage_class_code, home_region)
        retrieval_cost_per_gb = pricing.get_s3_retrieval_cost(storage_class_code, home_region)
        retrieval_requests_cost = pricing.get_s3_retrieval_req_cost(storage_class_code, home_region)
        df[storage_class] = [get_cost, retrieval_cost_per_gb, retrieval_requests_cost]
    return df

@st.experimental_fragment
def retrieval_components():
    retrieval_submitted = retrieval_form()
    if retrieval_submitted:
        total_size_MB = helper.convert_storage_size(st.session_state.size, st.session_state.unit, 'MB')

        if validate_retrieval_input(total_size_MB):

            total_size_retrieved = st.session_state.files_retrieval * st.session_state.size

            cols = st.columns(3)
            with cols[0]:
                ui.metric_card(title=f"Total size of each file", content=f"{st.session_state.size} {st.session_state.unit}", description="According to file size indicated above")
            with cols[1]:
                ui.metric_card(title="Total number of files to retrieve", content=f"{st.session_state.files_retrieval}", description="")
            with cols[2]:
                ui.metric_card(title="Total size of files to retrieve", content=f"{total_size_retrieved} {st.session_state.unit}", description=f"= total files * size of each file")

            stock_retrieval_df = get_retrieval_pricing()
            total_size_retrieved_gb = helper.convert_storage_size(total_size_retrieved, st.session_state.unit, 'GB')

            # Print table for stock cost first
            stock_table_df = stock_retrieval_df.map(lambda x: f'${x:.5f}')
            st.dataframe(stock_table_df, use_container_width=True)

            # Educate pricing
            st.info("""
                        Retrievals are charged according to data retrieval (`Retrieval Cost per GB`) and data requests incurred (`Retrieval Cost per 1000 Requests`).
                        For Amazon S3 Standard, no retrieval fee is charged.
                        For Amazon S3 Standard-Infrequent Access and S3 One Zone-Infrequent Access, data retrieval is charged.
                        For the 3 Amazon S3 Glacier classes, data retrieval and data requests are charged, according to the types of retrieval selected (Expedited, Standard, Bulk).
                        """)

            # Print table for total cost 
            table_df = pd.DataFrame(columns=st.session_state.selected_storage_class)
            table_df.loc[TOTAL_GET_REQUEST_COST] = stock_retrieval_df.loc[GET_REQUEST_COST] * st.session_state.files_retrieval
            table_df.loc[TOTAL_RETRIEVAL_COST] = stock_retrieval_df.loc[RETRIEVAL_COST] * total_size_retrieved_gb * st.session_state.files_retrieval
            table_df.loc[TOTAL_RETRIEVAL_REQUEST_COST] = stock_retrieval_df.loc[RETRIEVAL_REQUEST_COST] * math.ceil(st.session_state.files_retrieval/1000)
            table_df.loc[TOTAL_COST] = table_df.sum()
            table_df = table_df.map(lambda x: f'${x:.5f}')
            st.dataframe(table_df, use_container_width=True)

            df_long = table_df.reset_index()
            df_long = pd.melt(df_long, id_vars=['index'], var_name='Storage Class', value_name='Cost')

            fig = px.bar(df_long, x='index', y='Cost', color='Storage Class', barmode='group', labels={'Cost': 'Cost (USD)'})
            fig.update_yaxes(tickprefix="$")
            fig.update_xaxes(title_text="Cost Comparision between S3 Storage Classes")

            st.plotly_chart(fig, use_container_width=True)

            if any(element in GLACIER_CLASSES for element in st.session_state.selected_storage_class):
                st.info("""
                    Amazon S3 objects that are stored in the S3 Glacier Flexible Retrieval or S3 Glacier Deep Archive storage classes are not immediately accessible. 
                    To access an object in these storage classes, you must restore a temporary copy of the object to its S3 bucket for a specified duration (number of days). 
                    You pay for storage cost for both the archived object (per selected S3 Glacier class rates) and the copy that you restored temporarily (per S3 Standard rates).
                        """)

if __name__ == "__main__":

    add_page_title(layout="wide",)
    add_indentation()
    st.sidebar.selectbox("Select a Region:", pricing.region_code, key='home_region')
    home_region = st.session_state['home_region']

    retrieval_components()
        


