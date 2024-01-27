import pandas as pd
import plotly.express as px
import requests
from pathlib import Path

import streamlit as st
from streamlit_lottie import st_lottie
st.set_page_config(layout="wide", page_title="İstanbul Rail System App")

dataset_dir = (Path().resolve() / "data").absolute().as_posix()

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_metro_rail = load_lottieurl(
    "https://lottie.host/8443e5a3-be05-4150-8726-1de0e7bd1556/6zYgwu8qRy.json"
    
)
st_lottie(lottie_metro_rail, height=200)

st.title("Istanbul - Rail Systems Station Based Passage Numbers - 2022 Data set")
st.markdown("On this page you can analyze data by passage numbers.")

# Datasets
rail_lines = pd.read_csv(f"{dataset_dir}/processed_data_2022_rail_stations.csv")
tr_holidays = pd.read_csv(f"{dataset_dir}/tr_holidays.csv")

# Table
select_line = st.selectbox(
    "Select Line", rail_lines['line'].unique().tolist(),
    index=3
)
line_frame = rail_lines[rail_lines['line'] == select_line]
st.write(line_frame.head(5))

# Data frames for graph visualization
monthly_passenger_cnts = line_frame.groupby(['month', 
                                             'station_name']).agg(
                                             {'passage_cnt':'sum'})
monthly_passenger_cnts.reset_index(inplace=True)

age_frame = line_frame.groupby(['age']).agg({'passage_cnt':'sum'})
age_frame = age_frame.sort_values('passage_cnt')

weekly_passenger_cnts = line_frame.groupby(
                        ['date',
                         'month',
                         'week_number',
                         'day_of_week',
                         'station_name']).agg(
                            {'passage_cnt':'sum'})
weekly_passenger_cnts.reset_index(inplace=True)               

# Graphs 1 and 2
col1, col2 = st.columns(2)
with col1:
    st.write("Choose a month to see monthly passage counts by stations.")
    select_month = st.selectbox(
                    "Select Month",
                    rail_lines['month'].unique().tolist())
    month_passenger_cnts = monthly_passenger_cnts[monthly_passenger_cnts['month'] == select_month]
    fig_col1 = px.bar(month_passenger_cnts,
                      x='station_name',
                      y='passage_cnt',
                      title='Number of Passage by Stations',
                      color_discrete_sequence=['#7E7DCD']) 
    fig_col1.update_layout(xaxis_title='Stations',
                           yaxis_title='Passage Counts')
    st.plotly_chart(fig_col1)
with col2:
    st.write("Choose a public holiday date to see passage counts by stations.")
    select_public_holiday = st.selectbox(
                            "Select Public Holiday",
                            tr_holidays['Holiday'].tolist())
    holiday_date = tr_holidays[tr_holidays['Holiday'] == select_public_holiday]['Date'].values[0]
    holiday_passenger_cnt = line_frame[line_frame['date'] == holiday_date].groupby(
                                                                        ['station_name']).agg(
                                                                        {'passage_cnt':'sum'})
    fig_col2 = px.bar(holiday_passenger_cnt,
                x=holiday_passenger_cnt.index,
                y='passage_cnt',
                title=f'Number of Passage by Stations on {select_public_holiday}',
                color_discrete_sequence=['rgb(141,160,203)'])
    fig_col2.update_layout(xaxis_title='Stations',
                    yaxis_title='Passage Counts')
    st.plotly_chart(fig_col2)

# Graphs 3 and 4
col3, col4 = st.columns(2)
with col3:
    st.write("Choose an age group to see passage counts by stations.")
    select_age_group = st.selectbox(
                    "Select Age Group",
                     age_frame.index, index=3)
    age_st_frame = line_frame.groupby(['age', 'station_name']).agg({'passage_cnt':'sum'})
    age_st_frame.reset_index(inplace=True)
    age_group_st_frame = age_st_frame[age_st_frame['age'] == select_age_group]
    fig_col3 = px.bar(age_group_st_frame,
                      x='station_name',
                      y='passage_cnt',
                      title=f'Number of Passage by Stations for Group {select_age_group}',
                      color_discrete_sequence=['#9DA05A'])
    fig_col3.update_layout(xaxis_title='Stations',
                    yaxis_title='Passage Counts')
    st.plotly_chart(fig_col3)
    
with col4:
    st.write("Here you can see the number of passage by age group")
    st.write("")
    fig = px.pie(age_frame,
                    names=age_frame.index,
                    values='passage_cnt',
                    title='Number of Passage by Age Group',
                    color_discrete_sequence=px.colors.sequential.RdBu)
    fig.update_layout(margin=dict(t=40, b=0, l=80, r=0), legend_font_size=15)
    fig.update_traces(textfont_size=15)
    st.plotly_chart(fig)
    
# Last Graph
select_month_for_week = st.selectbox(
                    "Select Month for Week",
                    rail_lines['month'].unique().tolist())
select_week = st.selectbox(
                "Select Week",
                weekly_passenger_cnts['week_number'].unique().tolist())
week_psg_cnt = weekly_passenger_cnts[(weekly_passenger_cnts['month'] == select_month_for_week)
                                     & (weekly_passenger_cnts['week_number'] == select_week)]

min_date = week_psg_cnt['date'].min()
max_date = week_psg_cnt['date'].max()

fig = px.bar(week_psg_cnt,
             x='station_name',
             y='passage_cnt',
             color='day_of_week',
             title=f'Number of Passage for Each Day for Week ({min_date} - {max_date}) by Stations')
fig.update_layout(xaxis_title='Stations',
                 yaxis_title='Passage Counts')
st.plotly_chart(fig,use_container_width=True)

# caption
st.caption(
    """
    <div style="text-align:right;">
        <p>Built with Streamlit, by Hayriye Anıl 👻</p>
    </div>
    """,
    unsafe_allow_html=True
)
