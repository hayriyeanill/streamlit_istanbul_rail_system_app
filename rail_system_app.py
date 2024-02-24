import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from pathlib import Path

import streamlit as st
from streamlit_lottie import st_lottie
from st_pages import Page, show_pages
st.set_page_config(layout="wide", page_title="İstanbul Rail System App")

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_metro_rail = load_lottieurl(
    "https://lottie.host/8443e5a3-be05-4150-8726-1de0e7bd1556/6zYgwu8qRy.json"
    
)
st_lottie(lottie_metro_rail, height=200)

dataset_dir = (Path().resolve() / "data").absolute().as_posix()
show_pages(
    [
        Page("rail_system_app.py", "Passanger", ":metro:" ),
        Page("pages/passage_cnt.py", "Journey", ":station:"),
    ]
)

st.title('Istanbul - Rail Systems Station Based Passenger and Journey Numbers - 2022 Dataset')
st.markdown('<p style="font-size: 18px;">Hello and Welcome to the Istanbul Rail System Analysis App! 👋 </p>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 18px;">Use this Streamlit app to make your data analysis based on passanger or journey number for your chosen rail line. </p>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 18px;">This dataset obtained from the Istanbul Metropolitan Municipality Open Data Portal.</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 18px;">❗ This dataset was processed before analysis. You can access data and text processing codes on Github. </p>', unsafe_allow_html=True)

st.info('You can access the original dataset from [here](https://data.ibb.gov.tr/en/dataset/yas-grubuna-gore-rayli-sistemler-istasyon-bazli-yolcu-ve-yolculuk-sayilari/resource/8bed95de-bbe2-4550-80f2-87ca51a97f3d)', icon="ℹ️")
st.info('Since the latest dataset in the data portal is for 2022, this analysis was prepared using it.', icon="ℹ️")

####### DATASETS #######
rail_lines = pd.read_csv(f'{dataset_dir}/processed_data_2022_rail_stations.csv')
tr_holidays = pd.read_csv(f'{dataset_dir}/tr_holidays.csv')
stations_orders = pd.read_json(f'{dataset_dir}/lines_stations_orders.json')

####### SELECT RAIL LINE #######
st.subheader('Select Rail Line')
col1, col2 = st.columns(2)
with col1:
    st.markdown('''<p style="font-size: 18px;>">
            Choose a rail line from the dropdown menu and
            watch as map, table, and graphs transform! </p>''', unsafe_allow_html=True)
    select_line = st.selectbox("Select Line", rail_lines['line'].unique().tolist(),
                               label_visibility='collapsed',
                               index=3)
    
line_frame = rail_lines[rail_lines['line'] == select_line]

####### MAP #######
st.subheader('Location Map of Stations of the Rail Line')
st.markdown(f'''<p style="font-size: 18px;">
            Discover the station locations specific to {select_line} with this interactive map </p>''',
            unsafe_allow_html=True)

map_stations = stations_orders[stations_orders['line'] == select_line]['stations'].values[0]
map_df = line_frame.groupby(['latitude', 'longitude'])[['station_name']].first()
map_df.reset_index(inplace=True)
map_df.drop_duplicates('station_name', keep='first', inplace=True)
map_df.set_index('station_name', inplace=True)
filtered_map_df = map_df.reindex(map_stations)
filtered_map_df.dropna(inplace=True)
filtered_map_df.reset_index(inplace=True)

lat_lon_df = line_frame[['latitude', 'longitude', 'station_name']].drop_duplicates()
if lat_lon_df['latitude'].isna().any() and lat_lon_df['longitude'].isna().any():
    st.warning("""Warning: Since some stations in the selected rail system don't have
                  latitude and longitude information,
                  the station location may not appear on the map.""", icon="⚠️")

fig_map = px.scatter_mapbox(filtered_map_df,
                            lat='latitude',
                            lon='longitude',
                            color='station_name',
                            zoom=10,
                            mapbox_style="carto-positron",
                            )
fig_map.update_traces(marker={'size': 15})
fig_map.update_layout(
    margin=dict(l=20, r=20, t=15, b=20))
fig_map.add_trace(go.Scattermapbox(
    mode = "lines",
    lon = filtered_map_df['longitude'],
    lat = filtered_map_df['latitude'],
    showlegend=False,
    hoverinfo='skip'
))
st.plotly_chart(fig_map, use_container_width=True) 

####### INFO #######
st.subheader('Little Information about the Rail Line')

passenger_cnts_frame = line_frame.groupby(['date', 'station_name']).agg({'passanger_cnt': 'sum'})
passenger_cnts_frame.reset_index(inplace=True)
passanger_max_row = passenger_cnts_frame[
    passenger_cnts_frame['passanger_cnt'] == passenger_cnts_frame['passanger_cnt'].max()]
passanger_min_row = passenger_cnts_frame[
    passenger_cnts_frame['passanger_cnt'] == passenger_cnts_frame['passanger_cnt'].min()]

col1, col2, col3 = st.columns(3)

col1.metric(label="""Total number of passengers using this line""",
            value="{:,.0f}".format(passenger_cnts_frame['passanger_cnt'].sum()).replace(",", "."))

col1.metric(label="Total number of records for this line",
            value="{:,.0f}".format(line_frame.shape[0]).replace(",", "."))

col1.metric(label="Average number of passengers using this line",
            value="{:,.0f}".format(passenger_cnts_frame['passanger_cnt'].mean()).replace(",", "."))

col2.metric(label="Maximum number of passangers.",
            value="{:,.0f}".format(passanger_max_row['passanger_cnt'].values[0]).replace(",", "."))

col2.metric(label="The day with the highest number of passengers",
            value=pd.to_datetime(passanger_max_row['date'].values[0]).strftime('%d %B %Y'))

col2.metric(label="The station with the highest number of passengers",
            value=passanger_max_row['station_name'].values[0])

col3.metric(label="Minimum number of passangers",
            value=passanger_min_row['passanger_cnt'].values[0])

col3.metric(label="The day with the lowest number of passengers",
            value=pd.to_datetime(passanger_min_row['date'].values[0]).strftime('%d %B %Y'))

col3.metric(label="The station with the lowest number of passengers",
            value=passanger_min_row['station_name'].values[0])

####### DATA TABLE #######
st.markdown(f'''<p style="font-size: 18px;">
            Let see first 5 rows of the rail line frame</p>''',
            unsafe_allow_html=True)
st.write(line_frame.head(5))

####### GRAPH 1 #######
with st.container(border=True):
    st.subheader('Number of Passengers by Stations')
    monthly_passenger_cnts = line_frame.groupby(['month', 
                                                 'station_name']).agg(
                                             {'passanger_cnt':'sum'})
    monthly_passenger_cnts.reset_index(inplace=True)
    col1, col2 = st.columns(2)
    with col1:
        select_month = st.selectbox(
                        'Select Month',
                        rail_lines['month'].unique().tolist())
        month_passenger_cnts = monthly_passenger_cnts[monthly_passenger_cnts['month'] == select_month]
        max_passenger_per_month = monthly_passenger_cnts.loc[
            monthly_passenger_cnts.groupby('month')['passanger_cnt'].idxmax()]
        min_passenger_per_month = monthly_passenger_cnts.loc[
            monthly_passenger_cnts.groupby('month')['passanger_cnt'].idxmin()]          
             
        paragraph_maxs = max_passenger_per_month[max_passenger_per_month['month'] == select_month]
        paragraph_mins = min_passenger_per_month[min_passenger_per_month['month'] == select_month]
   
        fig_col1 = px.bar(month_passenger_cnts,
                            x='station_name',
                            y='passanger_cnt',
                            color_discrete_sequence=['rgb(57,105,172)'])
        fig_col1.update_layout(xaxis_title='Stations',
                                yaxis_title='Passanger Counts')
        st.plotly_chart(fig_col1, use_container_width=True)
    with col2:
             
        st.markdown('''<p style="text-align: center; font-size: 18px;">
                    Choose a month to see monthly passenger counts by stations.
                    In this chart, you can see the total number of passengers by stations
                    on this line according to the month you selected.''', unsafe_allow_html=True)
        
        st.markdown(f'''<p style="text-align: center; font-size: 18px;">
                    For example, in the month of {paragraph_maxs['month'].values[0]} you chose,
                    {paragraph_maxs['station_name'].values[0]} is the station with the highest number
                    of passengers with {paragraph_maxs['passanger_cnt'].values[0]:,} and
                    {paragraph_mins['station_name'].values[0]} is the station with the lowest number
                    of passengers with {paragraph_mins['passanger_cnt'].values[0]:,}.</p>''',
                    unsafe_allow_html=True)

####### GRAPH 2 #######     
with st.container(border=True):
    st.subheader('Number of Passengers by Stations on Public Holidays')
    col1, col2 = st.columns(2)
    with col1:
        select_public_holiday = st.selectbox(
                                "Select Public Holiday",
                                tr_holidays['Holiday'].tolist())
        holiday_date = tr_holidays[tr_holidays['Holiday'] == select_public_holiday]['Date'].values[0]
        holiday_passenger_cnt = line_frame[line_frame['date'] == holiday_date].groupby(
                                                                            ['station_name']).agg(
                                                                            {'passanger_cnt':'sum'})
        holiday_passenger_cnt.reset_index(inplace=True)                                                                   
        max_holiday_row = holiday_passenger_cnt[
            holiday_passenger_cnt['passanger_cnt'] == holiday_passenger_cnt['passanger_cnt'].max()]
        min_holiday_row = holiday_passenger_cnt[
            holiday_passenger_cnt['passanger_cnt'] == holiday_passenger_cnt['passanger_cnt'].min()]
        
        holidays_in_line_frame = line_frame[line_frame['date'].isin(tr_holidays['Date'].values.tolist())]
        sum_of_pass_in_holidays = holidays_in_line_frame.groupby(
            ['date', 'station_name']).agg({'passanger_cnt': 'sum'})
        sum_of_pass_in_holidays.reset_index(inplace=True)
        most_crowded_holiday = sum_of_pass_in_holidays[
            sum_of_pass_in_holidays['passanger_cnt'] == sum_of_pass_in_holidays['passanger_cnt'].max()]
        most_crowded_holiday_name = tr_holidays[tr_holidays['Date'] == most_crowded_holiday['date'].values[0]]['Holiday'].values[0]
        
        less_crowded_holiday = sum_of_pass_in_holidays[
            sum_of_pass_in_holidays['passanger_cnt'] == sum_of_pass_in_holidays['passanger_cnt'].min()]
        less_crowded_holiday_name = tr_holidays[tr_holidays['Date'] == less_crowded_holiday['date'].values[0]]['Holiday'].values[0]
        
        fig_col2 = px.bar(holiday_passenger_cnt,
                    x='station_name',
                    y='passanger_cnt',
                    color_discrete_sequence=['rgb(15,133,84)'])
        fig_col2.update_layout(xaxis_title='Stations',
                               yaxis_title='Passanger Counts')
        st.plotly_chart(fig_col2, use_container_width=True)
        
    with col2:
        st.markdown('''<p style="text-align: center; font-size: 18px;">
                    Choose a public holiday date to see passenger counts by stations.
                     In this chart, you can see the total number of passengers by stations
                     on this line according to the public holiday you selected.
                    </p>''',
                    unsafe_allow_html=True)  
        
        st.markdown(f'''<p style="text-align: center; font-size: 18px;">
                For example, in the public holiday of {select_public_holiday}
                {max_holiday_row['station_name'].values[0]} is the station with the highest number
                of passengers with {max_holiday_row['passanger_cnt'].values[0]:,} and
                {min_holiday_row['station_name'].values[0]} is the station with the lowest number
                of passengers with {min_holiday_row['passanger_cnt'].values[0]:,}.</p>''',
                unsafe_allow_html=True)
        
        st.markdown(f'''<p style="text-align: center; font-size: 18px;">
                    The most crowded holiday day was observed at 
                    {most_crowded_holiday['station_name'].values[0]}
                    Station on {pd.to_datetime(most_crowded_holiday['date'].values[0]).strftime('%d %B %Y')},
                    {most_crowded_holiday_name} with {most_crowded_holiday['passanger_cnt'].values[0]:,} passengers. </p>''',
                    unsafe_allow_html=True)
        
        st.markdown(f'''<p style="text-align: center; font-size: 18px;">
                    The less crowded holiday day was observed at 
                    {less_crowded_holiday['station_name'].values[0]} Station on
                    {pd.to_datetime(less_crowded_holiday['date'].values[0]).strftime('%d %B %Y')},
                    {less_crowded_holiday_name} with {less_crowded_holiday['passanger_cnt'].values[0]:,} passengers. </p>''',
                    unsafe_allow_html=True)
          
####### GRAPH 3 #######   
container = st.container()
with st.container(border=True):
    st.subheader('Number of Passangers by Stations on Age Groups')
    age_frame = line_frame.groupby(['age']).agg({'passanger_cnt':'sum'})
    age_frame = age_frame.sort_values('passanger_cnt')
    col1, col2 = st.columns(2)
    with col1:
        select_age_group = st.selectbox(
                        'Select Age Group',
                        age_frame.index, index=3)
        age_st_frame = line_frame.groupby(['age', 'station_name']).agg({'passanger_cnt':'sum'})
        age_st_frame.reset_index(inplace=True)
        age_group_st_frame = age_st_frame[age_st_frame['age'] == select_age_group]
        max_age_rows = age_st_frame.loc[age_st_frame.groupby('age')['passanger_cnt'].idxmax()]
        min_age_rows = age_st_frame.loc[age_st_frame.groupby('age')['passanger_cnt'].idxmin()]
        age_paragraph_maxs = max_age_rows[max_age_rows['age'] == select_age_group]
        age_paragraph_mins = min_age_rows[min_age_rows['age'] == select_age_group]
        
        fig_col3 = px.bar(age_group_st_frame,
                        x='station_name',
                        y='passanger_cnt',
                        color_discrete_sequence=['#924F4F'])
        fig_col3.update_layout(xaxis_title='Stations',
                        yaxis_title='Passanger Counts')
        st.plotly_chart(fig_col3, use_container_width=True)
    with col2:
        st.markdown('''<p style="text-align: center; font-size: 18px;">
                    Choose an age group and see how many passengers belong
                    to this age group by station.''', unsafe_allow_html=True)
        
        st.markdown(f'''<p style="text-align: center; font-size: 18px;">
                For example, passengers in the {select_age_group} age group you chose,
                {age_paragraph_maxs['station_name'].values[0]} station the most and 
                {age_paragraph_mins['station_name'].values[0]} station the least.</p>''',
                unsafe_allow_html=True)

####### GRAPH 4 #######
with st.container(border=True):
    st.subheader('Total Number of Passangers by Age Group')
    left, middle = st.columns((4, 6))
    with left:
        max_agegroup_row = age_frame[age_frame['passanger_cnt'] == age_frame['passanger_cnt'].max()]
        min_agegroup_row = age_frame[age_frame['passanger_cnt'] == age_frame['passanger_cnt'].min()]

        st.markdown('''<p style="text-align: center; font-size: 18px;">
                    In the pie chart on the side, you can see the percentages
                    of the age groups of the passengers using the line.</p>''', unsafe_allow_html=True)
        st.markdown(f'''<p style="text-align: center; font-size: 18px;">
                    According to the graph, the most crowded age group is {(max_agegroup_row.index).values[0]}
                    while the least crowded age group is {(min_agegroup_row.index).values[0]}.</p>''', unsafe_allow_html=True)
    with middle:
        fig = px.pie(age_frame,
                        names=age_frame.index,
                        values='passanger_cnt',
                        color_discrete_sequence=px.colors.sequential.RdBu)
        fig.update_layout(margin=dict(t=0, b=0, l=80, r=0), legend_font_size=15)
        fig.update_traces(textfont_size=15)
        st.plotly_chart(fig, use_container_width=True)

####### GRAPH 5 #######
st.subheader('Number of Passangers for Each Day for Selected Month and Week')
st.markdown('''<p style="font-size: 18px;">By selecting a month and a week in that month in this chart,
            you can see the total number of passengers visiting the stations
            on the days of that week.</p>''', unsafe_allow_html=True)

weekly_passenger_cnts = line_frame.groupby(
                        ['date',
                         'month',
                         'week_number',
                         'day_of_week',
                         'station_name']).agg(
                         {'passanger_cnt':'sum'})
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
             x='passanger_cnt',
             y='station_name', 
             color='day_of_week',
             orientation='h',
             height=800,
             title=f'Number of Passangers for Each Day for Week ({min_date} - {max_date}) by Stations')
fig.update_layout(xaxis_title='Stations',
                  yaxis_title='Passanger Counts')
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