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

st.title("Istanbul - Rail Systems Station Based Journey Numbers - 2022 Data set")
st.markdown("""<p style="font-size: 18px;">You can review the journeys made according to the selected rail line on this page.</p>""",
            unsafe_allow_html=True)

# Datasets
rail_lines = pd.read_csv(f"{dataset_dir}/processed_data_2022_rail_stations.csv")
tr_holidays = pd.read_csv(f"{dataset_dir}/tr_holidays.csv")
stations_orders = pd.read_json(f'{dataset_dir}/lines_stations_orders.json')

####### SELECT RAIL LINE #######
st.subheader('Select Rail Line')
col1, col2 = st.columns(2)
with col1:
    st.markdown('''<p style="font-size: 18px;>">
            Choose a rail line from the dropdown menu and
            watch graphs transform! </p>''', unsafe_allow_html=True)
    select_line = st.selectbox("Select Line", rail_lines['line'].unique().tolist(),
                               label_visibility='collapsed',
                               index=3)
    
line_frame = rail_lines[rail_lines['line'] == select_line]

####### INFO #######
st.subheader('Little Information about the Rail Line')

passage_cnts_frame = line_frame.groupby(['date', 'station_name']).agg({'passage_cnt': 'sum'})
passage_cnts_frame.reset_index(inplace=True)
passage_max_row = passage_cnts_frame[
    passage_cnts_frame['passage_cnt'] == passage_cnts_frame['passage_cnt'].max()]
passage_min_row = passage_cnts_frame[
    passage_cnts_frame['passage_cnt'] == passage_cnts_frame['passage_cnt'].min()]

col1, col2, col3 = st.columns(3)

col1.metric(label="""Total number of journeys using this line""",
            value="{:,.0f}".format(passage_cnts_frame['passage_cnt'].sum()).replace(",", "."))

col1.metric(label="Total number of records for this line",
            value="{:,.0f}".format(line_frame.shape[0]).replace(",", "."))

col1.metric(label="Average number of journeys using this line",
            value="{:,.0f}".format(passage_cnts_frame['passage_cnt'].mean()).replace(",", "."))

col2.metric(label="Maximum number of journeys.",
            value="{:,.0f}".format(passage_max_row['passage_cnt'].values[0]).replace(",", "."))

col2.metric(label="The day with the highest number of journeys",
            value=pd.to_datetime(passage_max_row['date'].values[0]).strftime('%d %B %Y'))

col2.metric(label="The station with the highest number of journeys",
            value=passage_max_row['station_name'].values[0])

col3.metric(label="Minimum number of journeys",
            value=passage_min_row['passage_cnt'].values[0])

col3.metric(label="The day with the lowest number of journeys",
            value=pd.to_datetime(passage_min_row['date'].values[0]).strftime('%d %B %Y'))

col3.metric(label="The station with the lowest number of journeys",
            value=passage_min_row['station_name'].values[0])


####### GRAPH 1 #######
with st.container(border=True):
    st.subheader('Number of Journeys by Stations')
    monthly_passenger_cnts = line_frame.groupby(['month', 
                                                 'station_name']).agg(
                                             {'passage_cnt':'sum'})
    monthly_passenger_cnts.reset_index(inplace=True)
    col1, col2 = st.columns(2)
    with col1:
        select_month = st.selectbox(
                        'Select Month',
                        rail_lines['month'].unique().tolist())
        month_passage_cnts = monthly_passenger_cnts[monthly_passenger_cnts['month'] == select_month]
        max_passage_per_month = monthly_passenger_cnts.loc[
            monthly_passenger_cnts.groupby('month')['passage_cnt'].idxmax()]
        min_passage_per_month = monthly_passenger_cnts.loc[
            monthly_passenger_cnts.groupby('month')['passage_cnt'].idxmin()]          
             
        paragraph_maxs = max_passage_per_month[max_passage_per_month['month'] == select_month]
        paragraph_mins = min_passage_per_month[min_passage_per_month['month'] == select_month]
   
        fig_col1 = px.bar(month_passage_cnts,
                            x='station_name',
                            y='passage_cnt',
                            color_discrete_sequence=['rgb(57,105,172)'])
        fig_col1.update_layout(xaxis_title='Stations',
                                yaxis_title='Journey Counts')
        st.plotly_chart(fig_col1, use_container_width=True)
    with col2:
             
        st.markdown('''<p style="text-align: center; font-size: 18px;">
                    Choose a month to see monthly journey counts by stations.
                    In this chart, you can see the total number of journeys by stations
                    on this line according to the month you selected.''', unsafe_allow_html=True)
        
        st.markdown(f'''<p style="text-align: center; font-size: 18px;">
                    For example, in the month of {paragraph_maxs['month'].values[0]} you chose,
                    {paragraph_maxs['station_name'].values[0]} is the station with the highest number
                    of journeys with {paragraph_maxs['passage_cnt'].values[0]:,} and
                    {paragraph_mins['station_name'].values[0]} is the station with the lowest number
                    of journeys with {paragraph_mins['passage_cnt'].values[0]:,}.</p>''',
                    unsafe_allow_html=True)

####### GRAPH 2 #######     
with st.container(border=True):
    st.subheader('Number of Journeys by Stations on Public Holidays')
    col1, col2 = st.columns(2)
    with col1:
        select_public_holiday = st.selectbox(
                                "Select Public Holiday",
                                tr_holidays['Holiday'].tolist())
        holiday_date = tr_holidays[tr_holidays['Holiday'] == select_public_holiday]['Date'].values[0]
        holiday_passage_cnt = line_frame[line_frame['date'] == holiday_date].groupby(
                                                                            ['station_name']).agg(
                                                                            {'passage_cnt':'sum'})
        holiday_passage_cnt.reset_index(inplace=True)                                                                   
        max_holiday_row = holiday_passage_cnt[
            holiday_passage_cnt['passage_cnt'] == holiday_passage_cnt['passage_cnt'].max()]
        min_holiday_row = holiday_passage_cnt[
            holiday_passage_cnt['passage_cnt'] == holiday_passage_cnt['passage_cnt'].min()]
        
        holidays_in_line_frame = line_frame[line_frame['date'].isin(tr_holidays['Date'].values.tolist())]
        sum_of_pass_in_holidays = holidays_in_line_frame.groupby(['date', 'station_name']).agg({'passage_cnt': 'sum'})
        sum_of_pass_in_holidays.reset_index(inplace=True)
        most_crowded_holiday = sum_of_pass_in_holidays[
            sum_of_pass_in_holidays['passage_cnt'] == sum_of_pass_in_holidays['passage_cnt'].max()]
        most_crowded_holiday_name = tr_holidays[tr_holidays['Date'] == most_crowded_holiday['date'].values[0]]['Holiday'].values[0]
        
        less_crowded_holiday = sum_of_pass_in_holidays[
            sum_of_pass_in_holidays['passage_cnt'] == sum_of_pass_in_holidays['passage_cnt'].min()]
        less_crowded_holiday_name = tr_holidays[tr_holidays['Date'] == less_crowded_holiday['date'].values[0]]['Holiday'].values[0]
        
        fig_col2 = px.bar(holiday_passage_cnt,
                    x='station_name',
                    y='passage_cnt',
                    color_discrete_sequence=['rgb(15,133,84)'])
        fig_col2.update_layout(xaxis_title='Stations',
                               yaxis_title='Journey Counts')
        st.plotly_chart(fig_col2, use_container_width=True)
        
    with col2:
        st.markdown('''<p style="text-align: center; font-size: 18px;">
                    Choose a public holiday date to see journey counts by stations.
                     In this chart, you can see the total number of journeys by stations
                     on this line according to the public holiday you selected.
                    </p>''',
                    unsafe_allow_html=True)  
        
        st.markdown(f'''<p style="text-align: center; font-size: 18px;">
                For example, in the public holiday of {select_public_holiday}
                {max_holiday_row['station_name'].values[0]} is the station with the highest number
                of journeys with {max_holiday_row['passage_cnt'].values[0]:,} and
                {min_holiday_row['station_name'].values[0]} is the station with the lowest number
                of journeys with {min_holiday_row['passage_cnt'].values[0]:,}.</p>''',
                unsafe_allow_html=True)
        
        st.markdown(f'''<p style="text-align: center; font-size: 18px;">
                    The most crowded holiday day was observed at 
                    {most_crowded_holiday['station_name'].values[0]}
                    Station on {pd.to_datetime(most_crowded_holiday['date'].values[0]).strftime('%d %B %Y')},
                    {most_crowded_holiday_name} with {most_crowded_holiday['passage_cnt'].values[0]:,} passages. </p>''',
                    unsafe_allow_html=True)
        
        st.markdown(f'''<p style="text-align: center; font-size: 18px;">
                    The less crowded holiday day was observed at 
                    {less_crowded_holiday['station_name'].values[0]} Station on
                    {pd.to_datetime(less_crowded_holiday['date'].values[0]).strftime('%d %B %Y')},
                    {less_crowded_holiday_name} with {less_crowded_holiday['passage_cnt'].values[0]:,} journeys. </p>''',
                    unsafe_allow_html=True)
          
####### GRAPH 3 #######   
container = st.container()
with st.container(border=True):
    st.subheader('Number of Journeys by Stations on Age Groups')
    age_frame = line_frame.groupby(['age']).agg({'passage_cnt':'sum'})
    age_frame = age_frame.sort_values('passage_cnt')
    col1, col2 = st.columns(2)
    with col1:
        select_age_group = st.selectbox(
                        'Select Age Group',
                        age_frame.index, index=3)
        age_st_frame = line_frame.groupby(['age', 'station_name']).agg({'passage_cnt':'sum'})
        age_st_frame.reset_index(inplace=True)
        age_group_st_frame = age_st_frame[age_st_frame['age'] == select_age_group]
        max_age_rows = age_st_frame.loc[age_st_frame.groupby('age')['passage_cnt'].idxmax()]
        min_age_rows = age_st_frame.loc[age_st_frame.groupby('age')['passage_cnt'].idxmin()]
        age_paragraph_maxs = max_age_rows[max_age_rows['age'] == select_age_group]
        age_paragraph_mins = min_age_rows[min_age_rows['age'] == select_age_group]
        
        fig_col3 = px.bar(age_group_st_frame,
                          x='station_name',
                          y='passage_cnt',
                          color_discrete_sequence=['#924F4F'])
        fig_col3.update_layout(xaxis_title='Stations',
                               yaxis_title='Journey Counts')
        st.plotly_chart(fig_col3, use_container_width=True)
    with col2:
        st.markdown('''<p style="text-align: center; font-size: 18px;">
                    Choose an age group and see how many journeys belong
                    to this age group by station.''', unsafe_allow_html=True)
        
        st.markdown(f'''<p style="text-align: center; font-size: 18px;">
                For example, passages in the {select_age_group} age group you chose,
                {age_paragraph_maxs['station_name'].values[0]} station the most and 
                {age_paragraph_mins['station_name'].values[0]} station the least.</p>''',
                unsafe_allow_html=True)

####### GRAPH 4 #######
with st.container(border=True):
    st.subheader('Total Number of Journeys by Age Group')
    left, middle = st.columns((4, 6))
    with left:
        max_agegroup_row = age_frame[age_frame['passage_cnt'] == age_frame['passage_cnt'].max()]
        min_agegroup_row = age_frame[age_frame['passage_cnt'] == age_frame['passage_cnt'].min()]

        st.markdown('''<p style="text-align: center; font-size: 18px;">
                    In the pie chart on the side, you can see the percentages
                    of the age groups of the journeys using the line.</p>''', unsafe_allow_html=True)
        st.markdown(f'''<p style="text-align: center; font-size: 18px;">
                    According to the graph, the most crowded age group is {(max_agegroup_row.index).values[0]}
                    while the least crowded age group is {(min_agegroup_row.index).values[0]}.</p>''', unsafe_allow_html=True)
    with middle:
        fig = px.pie(age_frame,
                     names=age_frame.index,
                     values='passage_cnt',
                     color_discrete_sequence=px.colors.sequential.RdBu)
        fig.update_layout(margin=dict(t=0, b=0, l=80, r=0), legend_font_size=15)
        fig.update_traces(textfont_size=15)
        st.plotly_chart(fig, use_container_width=True)

####### GRAPH 5 #######
st.subheader('Number of Journeys for Each Day for Selected Month and Week')
st.markdown('''<p style="font-size: 18px;">By selecting a month and a week in that month in this chart,
            you can see the total number of journeys of the stations
            on the days of that week.</p>''', unsafe_allow_html=True)

weekly_passenger_cnts = line_frame.groupby(
                        ['date',
                         'month',
                         'week_number',
                         'day_of_week',
                         'station_name']).agg(
                         {'passage_cnt':'sum'})
weekly_passenger_cnts.reset_index(inplace=True)     

col5, col6= st.columns(2)
with col5:
    select_month_for_week = st.selectbox(
                        'Select Month for Week',
                        rail_lines['month'].unique().tolist())
with col6:
    select_week = st.selectbox(
                    'Select Week',
                    weekly_passenger_cnts['week_number'].unique().tolist())
    
week_psg_cnt = weekly_passenger_cnts[(weekly_passenger_cnts['month'] == select_month_for_week)
                                     & (weekly_passenger_cnts['week_number'] == select_week)]
min_date = week_psg_cnt['date'].min()
max_date = week_psg_cnt['date'].max()

fig = px.bar(week_psg_cnt, 
             x='passage_cnt',
             y='station_name', 
             color='day_of_week',
             orientation='h',
             height=800,
             title=f'Number of Journeys for Each Day for Week ({min_date} - {max_date}) by Stations')
fig.update_layout(xaxis_title='Stations',
                  yaxis_title='Journey Counts')
st.plotly_chart(fig, use_container_width=True)

####### CAPTION #######
st.caption(
    '''
    <div style="text-align:right;">
        <p>Built with Streamlit, by Hayriye Anıl 👻</p>
    </div>
    ''',
    unsafe_allow_html=True
)