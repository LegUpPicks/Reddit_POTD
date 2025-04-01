import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar
import numpy as np
from streamlit_gsheets import GSheetsConnection

st.set_page_config(layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)
url_nim = "https://docs.google.com/spreadsheets/d/1H6vyNE7ufFom5absjZ6aG37ITjKeYumVLjPnTtwE6Zo/edit?usp=sharing"
df_nimzy = conn.read(spreadsheet=url_nim, usecols=[0, 1, 2, 3, 4, 5, 6, 7])
df_nimzy['Star'] = 'Nimzy'

url_kfalk = "https://docs.google.com/spreadsheets/d/1AxRj1wIxRT6exH5sYdiODNDJy9E5lNbQzp3KJjcOTT8/edit?usp=sharing"
df_kfalk = conn.read(spreadsheet=url_kfalk, usecols=[0, 1, 2, 3, 4, 5, 6, 7])
df_kfalk['Star'] = 'KFalker'

url_rip = "https://docs.google.com/spreadsheets/d/1Ek6QqNiKbx9bD45nG8cx1Kx0hT3OSrtJuBsIlpJ859k/edit?usp=sharing"
df_rip = conn.read(spreadsheet=url_rip, usecols=[0, 1, 2, 3, 4, 5, 6, 7])
df_rip['Star'] = 'RipRap'

url_cpa = "https://docs.google.com/spreadsheets/d/1Sbu2nlyHqpKD4S04fHqj5hIbYPvKMpqr6IGi2UqJUjo/edit?usp=sharing"
df_cpa = conn.read(spreadsheet=url_cpa, usecols=[0, 1, 2, 3, 4, 5, 6, 7])
df_cpa['Star'] = 'CPA_Poke'

url_jarid = "https://docs.google.com/spreadsheets/d/1Z562MfsoJyXdr-usiUEEokCdcDSpJ_CHi3oLwj238kw/edit?usp=sharing"
df_jarid = conn.read(spreadsheet=url_jarid, usecols=[0, 1, 2, 3, 4, 5, 6, 7])
df_jarid['Star'] = 'Jarid'

url_warren = "https://docs.google.com/spreadsheets/d/1Z562MfsoJyXdr-usiUEEokCdcDSpJ_CHi3oLwj238kw/edit?usp=sharing"
df_warren = conn.read(spreadsheet=url_warren, usecols=[0, 1, 2, 3, 4, 5, 6, 7])
df_warren['Star'] = 'Warren'

dfs = [df_nimzy, df_kfalk, df_rip, df_cpa, df_jarid, df_warren]
df_all = pd.concat(dfs)

# Reset index (optional, if you want a clean index)
df = df_all.reset_index(drop=True)

#st.dataframe(df)

df['Date'] = pd.to_datetime(df['Date'])

# Sidebar filters
Stars = df['Star'].unique()

# Make sure 'Jarid' is in the list or array
selected_Star = st.sidebar.selectbox(
    'Select Community Star', 
    options=['All'] + list(Stars)  # 'All' is always the first element
)

# Filter by Star
if selected_Star != 'All':
    df = df[df['Star'] == selected_Star]

# Sidebar: Filter by Sport
sports = df['Sport'].unique()
selected_sport = st.sidebar.selectbox('Select Sport', options=['All'] + list(sports))

# Filter by sport
if selected_sport != 'All':
    df = df[df['Sport'] == selected_sport]

# Date filter
date_range = st.sidebar.date_input("Select Date Range", [df['Date'].min(), df['Date'].max()])

if len(date_range) == 2:
    start_date, end_date = date_range
    df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
else:
    st.sidebar.warning("Please select both start and end dates.")

# Summary stats
w_count = (df['Win_Loss_Push'] == 'w').sum()
l_count = (df['Win_Loss_Push'] == 'l').sum()
p_count = (df['Win_Loss_Push'] == 'p').sum()
total_records = w_count + l_count + p_count  # Total wins, losses, and pushes

win_percentage = (w_count / total_records) * 100 if total_records > 0 else 0
total_units = df['Units_W_L'].sum()

# Display metrics
st.header("Summary Statistics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Wins", w_count)
    
with col2:
    st.metric("Total Losses", l_count)

with col3:
    st.metric("Total Pushes", p_count)

with col4:
    st.metric("Win Percentage", f"{win_percentage:.2f}%")

with col5:
    st.metric("Total Units", f"{total_units:.2f}")

# Create a DataFrame with Star-wise stats (WinPct and Units)
Star_stats = df.groupby('Star').agg(
    WinPct=('Win_Loss_Push', lambda x: (x == 'w').sum() / len(x) * 100),
    Units=('Units_W_L', 'sum')
).reset_index()

Star_stats['WinPct'] = Star_stats['WinPct'].round(2)
Star_stats['Units'] = Star_stats['Units'].round(2)

col1, col2 = st.columns(2)

# Display Star-wise stats table
with col1:
    st.subheader("Star Win Percentage and Units Total")
    st.dataframe(Star_stats.sort_values(by='Units', ascending=False))

with col2:
    current_date = pd.Timestamp.now()
    start_of_week = current_date - pd.Timedelta(days=current_date.weekday())
    start_of_week = start_of_week.normalize()
    df_this_week = df[df['Date'] >= start_of_week]
    df_this_week = df_this_week[df_this_week['Date'] <= current_date]
    Star_stats_current_week = df_this_week.groupby('Star').agg(
        WinPct=('Win_Loss_Push', lambda x: (x == 'w').sum() / len(x) * 100),
        Units=('Units_W_L', 'sum')
    ).reset_index()
    st.subheader("Star Win Percentage and Units Current Week")
    st.dataframe(Star_stats_current_week.sort_values(by='Units', ascending=False))

# Cumulative Units Calculation
df_cumulative = df.groupby('Date').agg({'Units_W_L': 'sum'}).cumsum().reset_index()
df_cumulative.rename(columns={'Units_W_L': 'Units'}, inplace=True)

# Create Daily Bar Chart using Plotly
df_daily_sum = df.groupby('Date')['Units_W_L'].sum().reset_index()
fig_daily = go.Figure()

fig_daily.add_trace(go.Bar(
    x=df_daily_sum['Date'],
    y=df_daily_sum['Units_W_L'],
    marker=dict(color=df_daily_sum['Units_W_L'].apply(lambda x: 'green' if x > 0 else 'red')),
    text=df_daily_sum['Units_W_L'].round(2),
    textposition='auto',
    hoverinfo='x+y+text',
))

fig_daily.update_layout(
    title='Daily Units Won / Lost',
    xaxis_title='Date',
    yaxis_title='Units Won / Lost',
    showlegend=False,
    template='plotly_white',
    xaxis_tickangle=-45,
)

# Create Weekly Bar Chart using Plotly
df['Week'] = df['Date'].dt.to_period('W-SUN').dt.start_time  # Convert dates to start of the week
df_weekly_sum = df.groupby('Week')['Units_W_L'].sum().reset_index()

fig_weekly = go.Figure()

fig_weekly.add_trace(go.Bar(
    x=df_weekly_sum['Week'],
    y=df_weekly_sum['Units_W_L'],
    marker=dict(color=df_weekly_sum['Units_W_L'].apply(lambda x: 'green' if x > 0 else 'red')),
    text=df_weekly_sum['Units_W_L'].round(2),
    textposition='auto',
    hoverinfo='x+y+text',
))

fig_weekly.update_layout(
    title='Weekly Units Won / Lost',
    xaxis_title='Week',
    yaxis_title='Units Won / Lost',
    showlegend=False,
    template='plotly_white',
    xaxis_tickangle=-45,
)

# Display the charts
st.plotly_chart(fig_weekly, key='weekly_chart')
st.plotly_chart(fig_daily, key='daily_chart')

# # Summary table
# summary_table = df.groupby('Sport')['Units_W_L'].sum().reset_index()
# summary_table.rename(columns={'Units_W_L': 'Units'}, inplace=True)
# summary_table['Units'] = summary_table['Units'].round(2)

# summary_table = summary_table.sort_values(by='Units', ascending=False)

# st.subheader("Units Summary by Sport")
# st.table(summary_table)

# # Calendar for daily units
# calendar_data = df.groupby(df['Date'].dt.date)['Units_W_L'].sum().reset_index()
# calendar_data['Date'] = pd.to_datetime(calendar_data['Date'])

# df = df.sort_values(by='Date', ascending=False)

# # Display full data
# st.header('Full Data')
# df['Date'] = df['Date'].dt.strftime('%m/%d/%Y')
# st.dataframe(df)

# # Create the cumulative plot
# fig = px.line(df_cumulative, x='Date', y='Units', title='Cumulative Units Over Time')

# # Display the plot
# st.plotly_chart(fig, key='cumulative_chart')
