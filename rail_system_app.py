import pandas as pd
import plotly.express as px
import requests
from pathlib import Path

import streamlit as st
from streamlit_lottie import st_lottie
from st_pages import Page, show_pages
st.set_page_config(layout="wide", page_title="İstanbul Rail System App")


dataset_dir = (Path().resolve() / "data").absolute().as_posix()
show_pages(
    [
        Page("rail_system_app.py", "Passanger", ":metro:" ),
        Page("pages/passage_cnt.py", "Passage", ":station:"),
    ]
)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_metro_rail = load_lottieurl(
    "https://lottie.host/8443e5a3-be05-4150-8726-1de0e7bd1556/6zYgwu8qRy.json"
    
)
st_lottie(lottie_metro_rail, height=200)

st.title("Istanbul - Rail Systems Station Based Passenger and Passage Numbers - 2022 Dataset")
st.markdown('Hello and Welcome to the Istanbul Rail System Analysis App! :wave:')
st.markdown("Use this Streamlit app to make your data analysis based on passanger or passage number for your chosen rail line.")
st.markdown("This dataset obtained from the Istanbul Metropolitan Municipality Open Data Portal. You can access the original dataset from [here](https://data.ibb.gov.tr/en/dataset/yas-grubuna-gore-rayli-sistemler-istasyon-bazli-yolcu-ve-yolculuk-sayilari/resource/8bed95de-bbe2-4550-80f2-87ca51a97f3d)")
st.markdown(":exclamation: This dataset was processed before analysis. You can access data and text processing codes on Github.")
st.info('Since the latest dataset in the data portal is for 2022, this analysis was prepared using it.', icon="ℹ️")

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

# Map
map_df = line_frame.groupby(['latitude', 'longitude'])[['station_name']].first()
map_df.reset_index(inplace=True)
map_df.drop_duplicates('station_name', keep='first', inplace=True)

lat_lon_df = line_frame[['latitude', 'longitude', 'station_name']].drop_duplicates()
if lat_lon_df['latitude'].isna().any() and lat_lon_df['longitude'].isna().any():
    st.warning("""Warning: Since some stations in the selected rail system don't have
                  latitude and longitude information,
                  the station location may not appear on the map.""", icon="⚠️")
    
fig_map = px.scatter_mapbox(map_df,
                            lat='latitude',
                            lon='longitude',
                            color='station_name',
                            zoom=10,
                            mapbox_style="carto-positron",
                            )
fig_map.update_traces(marker={'size': 15})
st.plotly_chart(fig_map, use_container_width=True)

# Data frames for graph visualization
monthly_passenger_cnts = line_frame.groupby(['month', 
                                             'station_name']).agg(
                                             {'passanger_cnt':'sum'})
monthly_passenger_cnts.reset_index(inplace=True)

age_frame = line_frame.groupby(['age']).agg({'passanger_cnt':'sum'})
age_frame = age_frame.sort_values('passanger_cnt')

weekly_passenger_cnts = line_frame.groupby(
                        ['date',
                         'month',
                         'week_number',
                         'day_of_week',
                         'station_name']).agg(
                         {'passanger_cnt':'sum'})
weekly_passenger_cnts.reset_index(inplace=True)               

# Graphs 1 and 2
col1, col2 = st.columns(2)
with col1:
    st.write("Choose a month to see monthly passenger counts by stations.")
    select_month = st.selectbox(
                    "Select Month",
                    rail_lines['month'].unique().tolist())
    month_passenger_cnts = monthly_passenger_cnts[monthly_passenger_cnts['month'] == select_month]
    fig_col1 = px.bar(month_passenger_cnts,
                      x='station_name',
                      y='passanger_cnt',
                      title='Number of Passengers by Stations',
                      color_discrete_sequence=['#7E7DCD'])
    fig_col1.update_layout(xaxis_title='Stations',
                           yaxis_title='Passanger Counts')
    st.plotly_chart(fig_col1)
with col2:
    st.write("Choose a public holiday date to see passenger counts by stations.")
    select_public_holiday = st.selectbox(
                            "Select Public Holiday",
                            tr_holidays['Holiday'].tolist())
    holiday_date = tr_holidays[tr_holidays['Holiday'] == select_public_holiday]['Date'].values[0]
    holiday_passenger_cnt = line_frame[line_frame['date'] == holiday_date].groupby(
                                                                        ['station_name']).agg(
                                                                        {'passanger_cnt':'sum'})
    fig_col2 = px.bar(holiday_passenger_cnt,
                x=holiday_passenger_cnt.index,
                y='passanger_cnt',
                title=f'Number of Passengers by Stations on {select_public_holiday}',
                color_discrete_sequence=['rgb(141,160,203)'])
    fig_col2.update_layout(xaxis_title='Stations',
                    yaxis_title='Passanger Counts')
    st.plotly_chart(fig_col2)

# Graphs 3 and 4
col3, col4 = st.columns(2)
with col3:
    st.write("Choose an age group to see passenger counts by stations.")
    select_age_group = st.selectbox(
                    "Select Age Group",
                     age_frame.index, index=3)
    age_st_frame = line_frame.groupby(['age', 'station_name']).agg({'passanger_cnt':'sum'})
    age_st_frame.reset_index(inplace=True)
    age_group_st_frame = age_st_frame[age_st_frame['age'] == select_age_group]
    fig_col3 = px.bar(age_group_st_frame,
                      x='station_name',
                      y='passanger_cnt',
                      title=f'Number of Passagers by Stations for Group {select_age_group}',
                      color_discrete_sequence=['#924F4F'])
    fig_col3.update_layout(xaxis_title='Stations',
                    yaxis_title='Passanger Counts')
    st.plotly_chart(fig_col3)
with col4:
    st.write("Here you can see the number of passangers by age group")
    st.write("")
    fig = px.bar(age_frame,
                    x=age_frame.index,
                    y='passanger_cnt',
                    title='Number of Passagers by Age Group')
    fig.update_traces(marker_color=['#ADD8E6',
                                    '#87CEEB',
                                    '#4682B4',
                                    '#483D8B',
                                    '#191970'])
    fig.update_layout(xaxis_title='Age Group',
                      yaxis_title='Passanger Counts')
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
             y='passanger_cnt',
             color='day_of_week',
             title=f'Number of Passagers for Each Day for Week ({min_date} - {max_date}) by Stations')
fig.update_layout(xaxis_title='Stations',
                 yaxis_title='Passanger Counts')
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