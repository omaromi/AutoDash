from decouple import config
# APIKEY = config('AIRTABLE_API_KEY')

from pyairtable import Table
from pyairtable.formulas import match
import pandas as pd
import plotly.express as px
import streamlit as st

# setting streamlit page configurations
st.set_page_config(
    page_title="Omar's Customizable Seekr Dashboard",
    page_icon="✅",
    layout="wide",
)

# defining function to remove list
# useful for transforming data later


def delist(x):
    return x[0]


# defining the whole operation to request and clean data from airtable into a workable dataframe

@st.experimental_memo(max_entries=2)
def get_data_to_df(inst="FY23 LearnUpon"):
    # base ID for CRD 1.5
    base_id = 'appFhUaPCtM80dgZY'

    # list of the fields I want to get out
    # this is important for reducing the size of the data request
    desired_fields = [
        'Name',
        'Milestone Name',
        'Interest_primary_proper',
        'A4',
        'Energy Score',
        'Predictability Score',
        'Salary Name',
        'User Profile Name',
        'Instance Name'
    ]

    filt = match({
        "Instance Name": inst
    })
    records = Table(st.secrets['AT_TOKEN'], base_id,
                    table_name='Diagnostic Results')
    data = records.all(formula=filt, fields=desired_fields)

    # flattening the dataframe
    df = pd.DataFrame.from_records(data)
    df_expected = pd.concat([df, df['fields'].apply(pd.Series)], axis=1).drop(
        ['fields', 'createdTime'], axis=1)

    # cleaning all the lookup fields from [x] to x
    df_expected['Energy Score'] = df_expected['Energy Score'].map(
        lambda x: delist(x), na_action='ignore')
    df_expected['Milestone Name'] = df_expected['Milestone Name'].map(
        lambda x: delist(x), na_action='ignore')
    df_expected['Salary Name'] = df_expected['Salary Name'].map(
        lambda x: delist(x), na_action='ignore')
    df_expected['Predictability Score'] = df_expected['Predictability Score'].map(
        lambda x: delist(x), na_action='ignore')
    df_expected['User Profile Name'] = df_expected['User Profile Name'].map(
        lambda x: delist(x), na_action='ignore')
    df_expected['Instance Name'] = df_expected['Instance Name'].map(
        lambda x: delist(x), na_action='ignore')
    # df_expected['Graduation Date'] = df_expected['Graduation Date'].map(
    #     lambda x: delist(x), na_action='ignore')

    return df_expected


# big_df = get_data_to_df(instance)

st.sidebar.header("Find your instance here")
instance = st.sidebar.selectbox(
    "Select Instance",
    ("Winter23 Fellowship Applicants", "FY23 LearnUpon",
     "W23 CUNY FIF Accelerator", "Summer 22 Fellowship Applicants")
)

big_df = get_data_to_df(instance)

new_df = big_df

st.title("A quick Fall 2022 Fellows Diagnostic Dashboard from Omar")

# filt = st.selectbox("Select the College", pd.unique(df_expected['College/University']))
# new_df = df_expected[df_expected['College/University'] == filt]

# filt = st.selectbox("Select the College", pd.unique(df_expected['Graduation Date']))
# new_df = df_expected[df_expected['Graduation Date'] == filt]

# milestone figures

milestone_order = ['Clarity', 'Alignment',
                   'Search Strategy', 'Interviewing & Advancing']

milestone_chart = new_df['Milestone Name'].value_counts().reset_index().rename(
    columns={'index': 'Milestone Score', 'Milestone Name': 'Number of Fellows'})

milestone_chart['Milestone Score'] = pd.Categorical(milestone_chart['Milestone Score'], [
                                                    x for x in milestone_order if x in milestone_chart['Milestone Score'].unique().tolist()], ordered=True)


milestones = milestone_chart.sort_values(by='Milestone Score')
figure_1 = px.bar(milestones, y='Milestone Score', x='Number of Fellows', color='Milestone Score', color_discrete_map={
                  'Clarity': "#00A3E1", 'Alignment': "#85C540", 'Search Strategy': "#D04D9D", 'Interviewing & Advancing': "#FFC507"})

st.markdown("### Milestone Distribution")
st.plotly_chart(figure_1, use_container_width=True)

# industry interest figures

interests = new_df['Interest_primary_proper'].value_counts(
).sort_index().reset_index()
figure_2 = px.bar(interests, x='Interest_primary_proper',
                  y='index', color='index')


st.markdown("### Industry Interest Distribution")
st.plotly_chart(figure_2, use_container_width=True)

# energy style figures

energy = new_df['Energy Score'].value_counts().reset_index().rename(
    columns={'index': 'Energy Label', 'Energy Score': 'Number of Fellows'})

# energy_order = ['Strong Introvert', 'Slight Introvert',
#                 'Ambivert', 'Slight Extrovert', 'Strong Extrovert']

# energy['Energy Label'] = pd.Categorical(energy['Energy Label'], [
#                                         x for x in energy_order if x in energy['Energy Label'].unique().tolist()], ordered=True)

energy_df = energy.sort_values(by='Energy Label')

figure_3 = px.bar(energy_df, x='Energy Label',
                  y='Number of Fellows', color='Energy Label')

# predictability figures

predict = new_df['Predictability Score'].value_counts().reset_index().rename(
    columns={'index': 'Predictability Label', 'Predictability Score': 'Number of Fellows'})

# predict_order = ['Structured', 'Any Work Environment', 'Flexible']

# predict['Predictability Label'] = pd.Categorical(predict['Predictability Label'], [
#                                                  x for x in predict_order if x in predict['Predictability Label'].unique().tolist()], ordered=True)

predict_df = predict.sort_values(by='Predictability Label')
figure_4 = px.bar(predict_df, x='Predictability Label',
                  y='Number of Fellows', color='Predictability Label')


# putting energy and predictability figures into columns
col1, col2 = st.columns(2)
with col1:
    st.markdown("#### Energy Style Summary")
    st.plotly_chart(figure_3, use_container_width=True)

with col2:
    st.markdown("#### Predictability Preference Summary")
    st.plotly_chart(figure_4, use_container_width=True)


# User profile figures
profiles = new_df['User Profile Name'].value_counts(
).reset_index().sort_index()
figure_5 = px.bar(profiles, x='index', y='User Profile Name', color='index')
st.plotly_chart(figure_5, use_container_width=True)

salary = new_df['Salary Name'].value_counts().reset_index().sort_index().rename(
    columns={'index': 'Salary Expectation', 'Salary Name': 'Number of Fellows'})
# salary_order = ['Salary Unsure', '40-60K', '60-80K', '80-100K', '100K+']

# salary['Salary Expectation'] = pd.Categorical(salary['Salary Expectation'], [
#                                               x for x in salary_order if x in salary['Salary Expectation'].unique().tolist()], ordered=True)

salary_df = salary.sort_values(by='Salary Expectation')
figure_6 = px.bar(salary_df, x='Salary Expectation',
                  y='Number of Fellows', color='Salary Expectation')


cola, colb = st.columns(2)

with cola:
    st.markdown("#### Salary Expectations")
    st.plotly_chart(figure_6, use_container_width=True)
    # st.metric("# of students unsure about their salary")
    st.markdown("""
    It is normal to see a significant number of students be unsure of what salary they can expect.
    """)
