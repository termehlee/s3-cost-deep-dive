import streamlit as st
import utils.pricing as pricing
from st_pages import show_pages_from_config, add_indentation, add_page_title, add_indentation
import streamlit_shadcn_ui as ui
import utils.helper as helper
import math
import pandas as pd
import numpy as np
import plotly.express as px  # interactive charts

LARGEST_FILE_SIZE = helper.convert_storage_size(5, 'TB', 'MB')
MAX_REQUESTS = 10000

def backup_form():
    with st.form('backup'):
        st.write("### Input the parameters for backup")
        size_col, unit_col = st.columns([3, 1])
        with size_col:
            st.number_input("Size of backup file", value=1, key='size')
        with unit_col:
            st.selectbox("Unit", ["GB", "TB"], index=1, key='unit')
        frequency_col, mpu_col = st.columns(2)
        with frequency_col:
            st.selectbox("Frequency of backup", ["Daily", "Weekly", "Monthly", "Yearly"], key='frequency')
        with mpu_col:
            st.slider("Multipart Upload Size", 5, 1024, 8, key='mpu_size')
        st.multiselect("Target storage classes for comparision", list(pricing.s3_storage_classes_excl_int), key='selected_storage_class')
        backup_submitted = st.form_submit_button("Submit")
    return backup_submitted

# @st.experimental_fragment
def validate_backup_input(total_size_MB, total_requests):
    # Validate maximum file size
    if total_size_MB > LARGEST_FILE_SIZE:
        st.error("File size is too large. Maximum file size allowed for upload to S3 is 5 TB.")
        return False
    
    # Validate storage classes selected
    if not st.session_state.selected_storage_class: 
        st.error("Please select at least one storage class")
        return False
    
    # Validate request count 
    if total_requests > MAX_REQUESTS:
        updated_multipart_size = math.ceil(total_size_MB / MAX_REQUESTS)
        st.warning(f"The maximum number of parts per upload is 10,000. Instead of selected MPU size of {st.session_state.mpu_size} MB, it is now {updated_multipart_size} MB.")
        st.session_state.total_requests = MAX_REQUESTS
        st.session_state.final_mpu_size = updated_multipart_size
    else:
        st.session_state.total_requests = total_requests
        st.session_state.final_mpu_size = st.session_state.mpu_size
    return True

# @st.experimental_fragment
def get_backup_pricing():
    df = pd.DataFrame(columns=st.session_state.selected_storage_class, index=['PUT Request Cost per Backup File', 'Storage Cost per GB-month'])
    st.info(f"For S3 Glacier Flexible Retrieval and Glacier Deep Archive, objects that are uploaded will incur S3 Standard PUT request pricing for parts, and the final complete multipart upload will incur the respective PUT pricing for that specific class.")

    for storage_class in st.session_state.selected_storage_class:
        storage_class_code =  pricing.s3_storage_classes[storage_class]
        cost_per_put = pricing.get_s3_put_cost(storage_class_code, home_region)

        # Glacier PUT cost is MPU with Standard cost, then complete MPU with Glacier cost
        if storage_class_code == 'GLACIER' or storage_class_code == 'DEEP_ARCHIVE':
            cost_per_mpu = pricing.get_s3_put_cost('STANDARD', home_region)
            put_cost = st.session_state.total_requests * cost_per_mpu + cost_per_put
        else:
            put_cost = st.session_state.total_requests * cost_per_put
        storage_cost_GB = pricing.get_s3_storage_cost(storage_class_code, home_region)
        df[storage_class] = [put_cost, storage_cost_GB]

    return df

def calculate_prorated_charge(df, column, size):
    retention = helper.get_retention(st.session_state.frequency)
    actual_retention = retention['actual']

    required_days = helper.get_prorated(column)
    cost_per_day = df.loc['CostGB-Day', column]
    print(required_days)
    
    if required_days - actual_retention <= 0:
        return 0.00
    else:
        return (required_days - actual_retention) * cost_per_day * size
    
@st.experimental_fragment
def backup_components(frequency, retention):
    cols = st.columns(2)
    with cols[0]:
        ui.metric_card(title=f"Retention period for {st.session_state.frequency} backups", content=f"Typically {retention['typical']}", description="Depending on compliance & backup types")
    with cols[1]:
        ui.metric_card(title="Number of PUT requests per file", content=f"{st.session_state.total_requests}", description=f"= File size / MPU size (or {MAX_REQUESTS} if the maximum number of parts is reached)")
    
    df = get_backup_pricing()
    
    numeric_cols = df.select_dtypes(include=np.number).columns
    df_stock = df.copy()
    df_stock = df_stock.map(lambda x: f'${x:.5f}')
    st.dataframe(df_stock, use_container_width=True)
    # df_stock = df_stock.round(-2)
    print(df_stock)

    # Calculate yearly cost
    total_size_GB = helper.convert_storage_size(st.session_state.size, st.session_state.unit, 'GB')
    df.loc['CostGB-Day'] = df.loc['Storage Cost per GB-month'] / 30
    df.loc['Yearly Total Storage Cost'] = df.loc['CostGB-Day'] * frequency * retention['actual'] * total_size_GB
    df.loc['Yearly Total PUT Requests Cost'] = df.loc['PUT Request Cost per Backup File'] * frequency
    df.loc['Pro-rated fee per file'] = [calculate_prorated_charge(df, column, total_size_GB) for column in df.columns]
    df.loc['Total pro-rated fee'] = df.loc['Pro-rated fee per file'] * frequency

    df.loc['Yearly Total Cost'] = df.loc['Yearly Total Storage Cost'] + df.loc['Yearly Total PUT Requests Cost'] + df.loc['Total pro-rated fee']
    st.info(f"Assuming retention period for {st.session_state.frequency} backups is {retention['actual']} days, the following table shows the yearly cost if data were to be deleted after the retention period expires.")

    numeric_cols = df.select_dtypes(include=np.number).columns
    df_yearly = df.copy()
    df_yearly.drop(index=['PUT Request Cost per Backup File', 'Storage Cost per GB-month', 'CostGB-Day'], inplace=True)
    # df_yearly[numeric_cols] = df_yearly[numeric_cols].map(lambda x: f'${x:.5f}')
    print(df_yearly)
    # df_yearly = df_yearly.round(2)
    df_yearly = df_yearly.map(lambda x: f'${x:.5f}')

    print(df_yearly)
    st.dataframe(df_yearly, use_container_width=True)
    st.warning(f"For certain storage classes, objects deleted prior to the minimum storage duration incur a pro-rated charge equal to the storage charge for the remaining days. The minimum storage duration is 30 days for S3 Standard-IA and S3 One Zone-IA, 90 days for S3 Glacier Instant Retrieval, Glacier Flexible Retrieval and 180 days for S3 Glacier Deep Archive")

    df_long = df_yearly.reset_index()
    df_long = pd.melt(df_long, id_vars=['index'], var_name='Storage Class', value_name='Cost')

    fig = px.bar(df_long, x='index', y='Cost', color='Storage Class', barmode='group', labels={'Cost': 'Cost (USD)'})
    fig.update_yaxes(tickprefix="$")
    fig.update_xaxes(title_text="Cost Comparision between S3 Storage Classes")

    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    add_page_title()
    add_indentation()


    st.title("Scenario #2: Hybrid - Backup & Restore")
    st.sidebar.selectbox("Select a Region:", pricing.region_code, key='home_region')

    home_region = st.session_state['home_region']

    backup_submitted = backup_form()

    if backup_submitted:
        total_size_MB = helper.convert_storage_size(st.session_state.size, st.session_state.unit, 'MB')
        total_requests = math.ceil(total_size_MB/st.session_state.mpu_size)

        if validate_backup_input(total_size_MB, total_requests):

            frequency = helper.get_frequency(st.session_state.frequency)
            retention = helper.get_retention(st.session_state.frequency)
            backup_components(frequency, retention)


