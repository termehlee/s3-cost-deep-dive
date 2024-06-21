import streamlit as st
import utils.pricing as pricing
from st_pages import show_pages_from_config, add_indentation, add_page_title
import pandas as pd

FREQUENT_ACCESS_TIER = f"Frequent Access Tier"
INFREQUENT_ACCESS_TIER = f"Infrequent Access Tier"
INSTANT_ACCESS_TIER = f"Archive Instant Access Tier"
ARCHIVE_ACCESS_TIER = f"Archive Access Tier"
DEEP_ARCHIVE_ACCESS_TIER = f"Deep Archive Access Tier"

TIP_IA = f"% of storage that hasn't been accessed in the last 30 days"
TIP_AI = f"% of storage that hasn't been accessed in the last 90 days"
def get_tip_archive():
    if st.session_state.activate_archive:
        return f"% of storage that hasn't been accessed for {st.session_state.archive_transition} days"
    else:
        return f"% of storage that hasn't been accessed for a minimum of 90 days"
def get_tip_deep():
    if st.session_state.activate_deep:
        return f"% of storage that hasn't been accessed for {st.session_state.deep_transition} days"
    else:
        return f"% of storage that hasn't been accessed for a minimum of 180 days"
    
TIP_ARCHIVE_ACCESS_TIER = f"When enabled, Intelligent-Tiering will automatically move objects that haven’t been accessed for a minimum of 90 days to the Archive Access tier."
TIP_DEEP_ARCHIVE_ACCESS_TIER = f"When enabled, Intelligent-Tiering will automatically move objects that haven’t been accessed for a minimum of 180 days to the Deep Archive Access tier."
ARCHIVE_ACCESS_ARCHIVE_INSTANT_COMPARISION = f"Only activate the Archive Access tier for 90 days if you want to bypass the Archive Instant Access tier."

ARCHIVE_ACCESS_TRANSITION = "Days until transition to the Archive Access tier"
TIP_ARCHIVE_ACCESS_TRANSITION = f"The number of consecutive days without access before tiering down to the Archive Access tier. Choose a whole number greater than or equal to 90 and up to 730 days"
DEEP_ARCHIVE_ACCESS_TRANSITION = "Days until transition to the Deep Archive Access tier"
TIP_DEEP_ARCHIVE_ACCESS_TRANSITION = f"The number of consecutive days without access before tiering down to the Deep Archive Access tier. Choose a whole number greater than or equal to 180 and up to 730 days"
ARCHIVE_AND_DEEP_ARCHIVE_WARNING = f"When both are selected, the Deep Archive Access tier transition value must be larger than the Archive Access tier transition value."
OPTIONAL = f"[Optional] "

PERCENTAGE_ERROR_MESSAGE = f"The sum of all enabled fields must equal 100%"

TOTAL_SIZE = f"Total size of all objects"
TOTAL_OBJECTS = f"Total number of objects"

ACCESS_TIERS = {
    'frequent': FREQUENT_ACCESS_TIER,
    'infrequent': INFREQUENT_ACCESS_TIER,
    'instant': INSTANT_ACCESS_TIER,
    'archive': ARCHIVE_ACCESS_TIER,
    'deep': DEEP_ARCHIVE_ACCESS_TIER
}

TRANSITION = {
    'frequent': "frequent_transition",
    'infrequent': "infrequent_transition",
    'instant': "instant_transition",
    'archive': "archive_transition",
    'deep': "deep_transition"
}

DAYS = f"Days till transition"
PERCENTAGE = f"% in "
COST_INCURRED = "Cost incurred"

def archive_options():
    cols = st.columns(2)
    with cols[0]:
        st.session_state.activate_archive = st.toggle(label=ARCHIVE_ACCESS_TIER, value=False)
        if st.session_state.activate_archive:
            st.info(TIP_ARCHIVE_ACCESS_TIER)
            st.number_input(label=ARCHIVE_ACCESS_TRANSITION, help=TIP_ARCHIVE_ACCESS_TRANSITION, min_value=90, max_value=730, value=90, step=1, key='archive_transition')
            st.info(ARCHIVE_ACCESS_ARCHIVE_INSTANT_COMPARISION)
            if st.session_state.archive_transition == 90:
                st.session_state.disable_instant = True
    with cols[1]:
        st.session_state.activate_deep = st.toggle(label=DEEP_ARCHIVE_ACCESS_TIER, value=False)
        if st.session_state.activate_deep:
            st.info(TIP_DEEP_ARCHIVE_ACCESS_TIER)
            st.number_input(label=DEEP_ARCHIVE_ACCESS_TRANSITION, help=TIP_DEEP_ARCHIVE_ACCESS_TRANSITION, min_value=180, max_value=730, value=180, step=1, key='deep_transition')
    
    if st.session_state.activate_archive and st.session_state.activate_deep:
        st.warning(ARCHIVE_AND_DEEP_ARCHIVE_WARNING)

def access_form():
    with st.form('access'):
        num_col, size_col, unit_col = st.columns([2, 2, 1])
        with num_col:
            st.number_input("Number of objects", value=1000, key='num', min_value=1)
        with size_col:
            st.number_input("Average size of object", value=1, key='size', min_value=1)
        with unit_col:
            st.selectbox("Unit", ['KB', 'MB', 'GB', 'TB'], index=1, key='unit')

        fa_col, ia_col, ai_col, a_col, da_col= st.columns(5)
        with fa_col:
            st.number_input(PERCENTAGE + FREQUENT_ACCESS_TIER, min_value=0, step=1, key='frequent')
        with ia_col:
            st.number_input(PERCENTAGE + INFREQUENT_ACCESS_TIER, min_value=0, step=1, help=TIP_IA, key='infrequent')
        with ai_col:
            st.number_input(PERCENTAGE + INSTANT_ACCESS_TIER, min_value=0, step=1, help=TIP_AI, key='instant', disabled=st.session_state.disable_instant)
        with a_col:
            st.number_input(PERCENTAGE + ARCHIVE_ACCESS_TIER, min_value=0, step=1, help=OPTIONAL + get_tip_archive(), key='archive', disabled=not st.session_state.activate_archive)
        with da_col:
            st.number_input(PERCENTAGE + DEEP_ARCHIVE_ACCESS_TIER, min_value=0, step=1, help=OPTIONAL + get_tip_deep(), key='deep', disabled=not st.session_state.activate_deep)
        access_submitted = st.form_submit_button("Submit")
    return access_submitted

def validate_form():
    tiers = ["frequent", "infrequent", "instant"]

    if st.session_state.activate_archive:
        tiers.append("archive")

    if st.session_state.activate_deep:
        tiers.append("deep")

    if st.session_state.disable_instant:
        tiers.remove("instant")

    total_percentage = 0

    for item in tiers:
        total_percentage += st.session_state[item]

    if total_percentage != 100:
        st.session_state.error_message = PERCENTAGE_ERROR_MESSAGE
    elif st.session_state.archive_transition >= st.session_state.deep_transition:
        st.session_state.error_message = ARCHIVE_AND_DEEP_ARCHIVE_WARNING
    else:
        st.session_state.error_message = None
        st.session_state.tiers = tiers

def metric_component():
    tiers = st.session_state.tiers
    with st.container(border=True):
        st.subheader("Time taken to transition to selected access tiers:")
        cols = st.columns(len(tiers))
        for item in tiers:
            with cols[tiers.index(item)]:
                st.metric(label=f"{ACCESS_TIERS[item]}", value=f"{st.session_state[TRANSITION[item]]} days")

def get_int_pricing():
    df = pd.DataFrame(columns=[COST_INCURRED], index=st.session_state.tiers)
    for item in st.session_state.tiers:
        df.loc[ACCESS_TIERS[item]] = pricing.get_s3_int_storage_cost(item, st.session_state[TRANSITION[item]])

# def access_components():

    
if __name__ == "__main__":
    add_page_title(layout="wide")
    add_indentation()
    st.sidebar.selectbox("Select a Region:", pricing.region_code, key='home_region')
    home_region = st.session_state['home_region']

    if "diable_instant" not in st.session_state:
        st.session_state.disable_instant = False
    
    if "archive_transition" not in st.session_state:
        st.session_state.archive_transition = 90
        st.session_state.deep_transition = 180
        st.session_state.infrequent_transition = 30
        st.session_state.instant_transition = 90
        st.session_state.frequent_transition = 0

    archive_options()
    access_submitted = access_form()
    
    if access_submitted:
        validate_form()
        if st.session_state.error_message is not None:
            st.error(f"{st.session_state.error_message}")
        else:
            metric_component()
            # access_components()
