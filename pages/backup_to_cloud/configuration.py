import streamlit as st
import utils.helper as helper
import utils.pricing as pricing
import streamlit_shadcn_ui as ui
import pandas as pd
import plotly.express as px  # interactive charts
import math
from st_pages import show_pages_from_config, add_page_title, add_indentation

add_indentation()

# st.set_page_config(page_title="Backup to Cloud", page_icon="☁️", layout="wide")
st.title("Scenario #1: Backup to Cloud")
st.sidebar.selectbox("Select a Region:", pricing.region_code, key='home_region')
print(st.session_state['home_region'])
# Collect input parameters
form = st.form("input")
home_region = st.session_state['home_region']
with form:
    st.write("### Input the parameters")
    size_col, unit_col = st.columns([3, 1])
    with size_col:
        size = st.number_input("Size of total backup data", value=1)
    with unit_col:
        unit = st.selectbox("Unit", ["GB", "TB", "PB"], index=1)
    # frequency = st.selectbox("Frequency of backup", ["Daily", "Weekly", "Monthly", "Yearly"])
    dedupe_col, multipart_col = st.columns([2, 2])
    with dedupe_col:
        deduplication = st.slider("% Data Deduplication", 0, 100, 25)
    with multipart_col:
        multipart_size = st.slider("Multipart Upload Size", 32, 1024, 64)
    selected_storage_class = st.multiselect("Target storage classes for comparision", list(pricing.s3_storage_classes))

submitted = form.form_submit_button("Submit")
print(selected_storage_class)
if submitted:
    if not selected_storage_class: 
        st.error("Please select at least one storage class")
    else:
        total_size = size * ((100 - deduplication) / 100)

        # Create df for costing
        df = pd.DataFrame(columns=selected_storage_class, index=['PUT Request Cost'])
        total_size_MB = helper.convert_storage_size(total_size, unit, 'MB')
        total_requests = math.ceil(total_size_MB/multipart_size)
        cols = st.columns(2)
        with cols[0]:
            ui.metric_card(title="Total size after deduplication", content=f'{total_size} {unit}', description="Total size * (100 - deduplication %)", key="card1")
        with cols[1]:
            ui.metric_card(title="Total number of PUT requests", content=f"{total_requests}", description="Total size after deduplication / MPU size", key="card2")

        for storage_class in selected_storage_class:
            storage_class_code =  pricing.s3_storage_classes[storage_class]
            cost_per_put = pricing.get_s3_put_cost(storage_class_code, home_region)
            print(total_requests)
            cost = total_requests * cost_per_put
            df[storage_class] = [cost]

        df_reset = df.reset_index()
        df_long = pd.melt(df_reset, id_vars=['index'], var_name='Storage Class', value_name='Cost')
        df_long['Cost'] = df_long['Cost'].map('${:.5f}'.format)

        df_wo_index = df_long.drop(columns='index')
        st.dataframe(df_wo_index, use_container_width=True, hide_index=True)
        #Print chart
        fig = px.bar(df_long, x='index', y='Cost', color='Storage Class', barmode='group', labels={'Cost': 'Cost (USD)'})
        print(df_long)
        fig.update_yaxes(tickformat=".6f")
        fig.update_yaxes(tickprefix="$")
        fig.update_xaxes(title_text="Cost Comparision between S3 Storage Classes")

        st.plotly_chart(fig, use_container_width=True)