import streamlit as st
import utils.pricing as pricing
from st_pages import show_pages_from_config, add_indentation, add_page_title
import streamlit_shadcn_ui as ui
import pandas as pd
import numpy as np
import utils.helper as helper
import plotly.express as px  # interactive charts

STORAGE_COST = "Storage cost per GB-month"
TRANSITION_COST = "Transition request cost per 1000 request"
TOTAL_COST = 'Total cost'
TOTAL_TRANSITION_COST = "Total transition request cost"
COST_INCURRED = "Cost incurred"
CALCULATIONS = "Calculations"
AVG_OBJ_SIZE = "Average object size"
TOTAL_OBJ_COUNT = "Total number of objects"
DAYS_AFT_CREATION = "Days after object creation"
TOTAL_SIZE = "Total size of objects (GB)"
S3_INT = "S3 Intelligent-Tiering"
S3_INT_WARNING = "Note: For S3 Intelligent-Tiering, this scenario only takes into account the storage cost in the Frequent Access Tier. Refer to the next module for a more complete scenario."

def validate_target_selection():
    # Validate source target
    if st.session_state.target is None:
        st.session_state.error_message = "Please select a target storage class"
    
    # # Validate waterfall target
    # else:
    #     avail_target = pricing.s3_storage_classes_waterfall[st.session_state.source]
    #     if st.session_state.target not in avail_target:
    #         st.session_state.error_message = f"You are not able to transition items from {st.session_state.source} to {st.session_state.target}. Please choose the target storage class as any of these instead: {', '.join(avail_target)}"
    else:
        st.session_state.error_message = None

def access_form():

    with st.form('access'):
        st.write("### Input the parameters for known data access patterns")
        num_col, size_col, unit_col = st.columns([2, 2, 1])
        with num_col:
            st.number_input("Number of objects", value=1000, key='num', min_value=1)
        with size_col:
            st.number_input("Average size of object", value=1, key='size', min_value=1)
        with unit_col:
            st.selectbox("Unit", ['KB', 'MB', 'GB', 'TB'], index=1, key='unit')
        object_col, forecast_col = st.columns(2)
        with object_col:
            st.slider("Days after object creation", 0, 365, 30, key='days')
        with forecast_col:
            st.slider("Days to forecast", 0, 720, 30, key='forecast')
        access_submitted = st.form_submit_button("Submit")
    return access_submitted

def get_access_pricing():
    df = pd.DataFrame(columns=[st.session_state.source, st.session_state.target], index=[STORAGE_COST, TRANSITION_COST])
    source_storage_class_code = pricing.s3_storage_classes[st.session_state.source]
    target_storage_class_code =  pricing.s3_storage_classes[st.session_state.target]
    
    # Get source pricing
    df[st.session_state.source] = [pricing.get_s3_storage_cost(source_storage_class_code, home_region), np.nan]
    df[st.session_state.target] = [pricing.get_s3_storage_cost(target_storage_class_code, home_region), pricing.get_s3_transition_cost(target_storage_class_code, home_region)]
    print(df)
    return df

def access_components():
    cols = st.columns(3)
    with cols[0]:
        st.metric(label=f"{AVG_OBJ_SIZE}", value=f"{st.session_state.size} {st.session_state.unit}")
    with cols[1]:
        st.metric(label=f"{TOTAL_OBJ_COUNT}", value=f"{st.session_state.num}")
    with cols[2]:
        st.metric(label="Days after object creation", value=f"{st.session_state.days}")

    df = get_access_pricing()

    total_size_transitioned = st.session_state.size * st.session_state.num
    total_size_transitioned_gb = helper.convert_storage_size(total_size_transitioned, st.session_state.unit, 'GB')
    remaining_days = st.session_state.forecast - st.session_state.days
    print("here", total_size_transitioned_gb)
    SOURCE_STORAGE_COST = f"{st.session_state.source} storage cost until {st.session_state.days} days"
    TARGET_STORAGE_COST = f"{st.session_state.target} storage cost for remaining {remaining_days} days"
    
    cost_df = pd.DataFrame(columns=[COST_INCURRED], index=[SOURCE_STORAGE_COST, TARGET_STORAGE_COST, TOTAL_TRANSITION_COST, TOTAL_COST])

   # Get total cost incurred after transitioning
    cost_df.loc[SOURCE_STORAGE_COST] = (df.loc[STORAGE_COST, st.session_state.source] / 30) * st.session_state.days * total_size_transitioned_gb
    cost_df.loc[TARGET_STORAGE_COST] = (df.loc[STORAGE_COST, st.session_state.target] / 30) * (remaining_days) * total_size_transitioned_gb
    cost_df.loc[TOTAL_TRANSITION_COST] = df.loc[TRANSITION_COST, st.session_state.target] * st.session_state.num
    cost_df.loc[TOTAL_COST] = cost_df.loc[[SOURCE_STORAGE_COST, TARGET_STORAGE_COST, TOTAL_TRANSITION_COST], COST_INCURRED].sum()

    cost_df = cost_df[COST_INCURRED].map(lambda x: f'${x:.5f}')

    # Transition container
    with st.container(border=True):
        st.write(f"Total cost to transition objects from {st.session_state.source} to {st.session_state.target} after {st.session_state.days} days")
        st.dataframe(cost_df, use_container_width=True)

        # Writing equations
        source_equation = fr'''$
            \scriptsize\text{{{SOURCE_STORAGE_COST}}} = \frac{{\text{{{STORAGE_COST}}}\, (\text{{{st.session_state.source}}})}}{{\text{{30 days in a month}}}} * \text{st.session_state.days} \text{{ days}} * \text{{{TOTAL_SIZE}}}
            $'''
        target_equation = fr'''$
            \scriptsize\text{{{TARGET_STORAGE_COST}}} = \frac{{\text{{{STORAGE_COST}}}\, (\text{{{st.session_state.target}}})}}{{\text{{30 days in a month}}}} * (\text{{{st.session_state.forecast - st.session_state.days}}} \text{{ days}}) * \text{{{TOTAL_SIZE}}}
            $'''
        transition_equation = fr'''$
            \scriptsize\text{{{TOTAL_TRANSITION_COST}}} = \frac{{\text{{{TRANSITION_COST}}}}}{{\text{{1000 requests}}}} \times \text{{{TOTAL_OBJ_COUNT}}}
            $'''
        total_equation = fr'''$
            \scriptsize\text{{{TOTAL_COST}}} = \text{{{SOURCE_STORAGE_COST}}} + \text{{{TARGET_STORAGE_COST}}} + \text{{{TOTAL_TRANSITION_COST}}}
            $'''
        st.write(source_equation)
        st.write(target_equation)
        st.write(transition_equation)
        st.write(total_equation)
    
    if st.session_state.target == S3_INT or st.session_state.source == S3_INT:
        st.info(S3_INT_WARNING)

    # Original storage container
    ORIGINAL_STORAGE_COST = f"{st.session_state.source} storage cost for {st.session_state.forecast} days"
    original_df = pd.DataFrame(columns=[COST_INCURRED], index=[ORIGINAL_STORAGE_COST])
    original_df.loc[ORIGINAL_STORAGE_COST] = (df.loc[STORAGE_COST, st.session_state.source] / 30) * st.session_state.forecast * total_size_transitioned_gb
    original_df = original_df.map(lambda x: f'${x:.5f}')
    
    with st.container(border=True):
        # Get original cost incurred if never transition
        st.write(f"Total cost for objects to remain in {st.session_state.source} for {st.session_state.forecast} days")
        st.dataframe(original_df, use_container_width=True)
        original_equation = fr'''$
            \scriptsize\text{{{ORIGINAL_STORAGE_COST}}} = \frac{{\text{{{STORAGE_COST}}}\, (\text{{{st.session_state.source}}})}}{{\text{{30 days in a month}}}} * \text{{{st.session_state.forecast}}} \text{{ days}} * \text{{{TOTAL_SIZE}}}
            $'''
        st.write(original_equation)

    transition_total_cost = cost_df.loc[TOTAL_COST]
    original_total_cost = original_df.at[ORIGINAL_STORAGE_COST, COST_INCURRED]
    comparison_df = pd.DataFrame({COST_INCURRED: [transition_total_cost, original_total_cost]}, index=['Lifecycle Total Cost', 'Original Total Cost'])
    fig = px.bar(comparison_df, x=comparison_df.index, y=COST_INCURRED, title='Comparison of Values')
    fig.update_yaxes(tickprefix="$")
    fig.update_xaxes(title_text="Cost Comparision")
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    add_page_title(layout="wide")
    add_indentation()
    # st.set_page_config(page_title="Hybrid Cloud", page_icon="☁️", layout="wide")
    # st.title("Scenario #3: Data Lake")
    st.sidebar.selectbox("Select a Region:", pricing.region_code, key='home_region')

    home_region = st.session_state['home_region']

    if "source" not in st.session_state:
        st.session_state.source = list(pricing.s3_storage_classes.keys())[0]

    if "target" not in st.session_state:
        st.session_state.target = None
    
    # Selection of lifecycle actions
    with st.container(border=True):
        source_col, target_col = st.columns(2)
        with source_col:
            st.selectbox("Source storage class", list(pricing.s3_storage_classes.keys()), index=0, key='source')
        with target_col:
            allowed_class = pricing.s3_storage_classes_waterfall[st.session_state.source]
            st.selectbox("Target storage class", list(allowed_class), index=0, key='target')
    access_submitted = access_form()

    if access_submitted:
        validate_target_selection()
        if st.session_state.error_message is not None:
            st.error(f"{st.session_state.error_message}")
        else:
            access_components()

    print(st.session_state)