import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Cornell Tech Weather',
    page_icon=':sunny:', # This is an emoji shortcode. Could be a URL too.
    layout="wide"
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_weather_data():
    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/weather.csv'
    df = pd.read_csv(DATA_FILENAME)
    
    # Convert to datetime and calculate Fahrenheit
    df['time'] = pd.to_datetime(df['time'])
    df['year'] = df['time'].dt.year
    df['month'] = df['time'].dt.month
    df['day_of_year'] = df['time'].dt.dayofyear
    df['Ftemp'] = (df['Ktemp'] - 273.15) * (9/5) + 32
    
    return df

df = get_weather_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :sunny: Cornell Tech Weather Dashboard

Explore historical temperature data at Cornell Tech from 1950 to present. This interactive dashboard allows you 
to visualize temperature patterns and trends over time.
'''

# Add some spacing
''
''

# Sidebar for controls
st.sidebar.header('Visualization Controls')
viz_type = st.sidebar.radio(
    'Visualization Type',
    ['Monthly Averages', 'Heatmap']
)

# Display different visualizations based on selection
if viz_type == 'Heatmap':
    st.header('Temperature Heatmap', divider='gray')
    
    # Move controls from sidebar to main content area
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Year range slider
        min_year = int(df['year'].min())
        max_year = int(df['year'].max())
        
        year_range = st.slider(
            'Year Range',
            min_value=min_year,
            max_value=max_year,
            value=[min_year, max_year])
    
    with col2:
        # Season selection
        seasons = ['All Year', 'Winter (Dec-Feb)', 'Spring (Mar-May)', 'Summer (Jun-Aug)', 'Fall (Sep-Nov)']
        selected_season = st.selectbox('Season', seasons)
    
    with col3:
        # Color scale selection
        color_scales = ['RdBu_r', 'Viridis', 'Plasma', 'Inferno', 'Turbo']
        selected_colorscale = st.selectbox('Color Scale', color_scales)
    
    # Filter data based on year range
    filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    
    # Filter data based on season if needed
    if selected_season == 'Winter (Dec-Feb)':
        filtered_df = filtered_df[((filtered_df['month'] == 12) | (filtered_df['month'] <= 2))]
    elif selected_season == 'Spring (Mar-May)':
        filtered_df = filtered_df[(filtered_df['month'] >= 3) & (filtered_df['month'] <= 5)]
    elif selected_season == 'Summer (Jun-Aug)':
        filtered_df = filtered_df[(filtered_df['month'] >= 6) & (filtered_df['month'] <= 8)]
    elif selected_season == 'Fall (Sep-Nov)':
        filtered_df = filtered_df[(filtered_df['month'] >= 9) & (filtered_df['month'] <= 11)]
    
    # Create pivot table for heatmap
    heatmap_data = filtered_df.groupby(['year', 'day_of_year'])['Ftemp'].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='year', columns='day_of_year', values='Ftemp')
    
    # Month positions for x-axis
    month_positions = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Create the heatmap using plotly express
    fig = px.imshow(
        heatmap_pivot, 
        labels=dict(x="Day of Year", y="Year", color="Temperature (°F)"),
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        color_continuous_scale=selected_colorscale,
        aspect="auto"
    )
    
    # Update layout for better appearance
    fig.update_layout(
        xaxis_title='Day of Year',
        yaxis_title='Year',
        height=700,
    )
    
    # Create custom x-axis (months instead of days)
    fig.update_xaxes(
        tickvals=month_positions,
        ticktext=month_labels,
    )
    
    # Create custom y-axis (show every 5 years)
    years = heatmap_pivot.index.tolist()
    year_ticks = [year for year in years if year % 5 == 0]
    fig.update_yaxes(
        tickvals=year_ticks,
        ticktext=[str(year) for year in year_ticks],
    )
    
    # Add hover information to display exact values
    fig.update_traces(
        hovertemplate="Year: %{y}<br>Day: %{x}<br>Temperature: %{z:.1f}°F<extra></extra>"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display statistics
    st.subheader("Temperature Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        avg_temp = filtered_df['Ftemp'].mean()
        st.metric("Average Temperature", f"{avg_temp:.1f}°F")
    with col2:
        max_temp = filtered_df['Ftemp'].max()
        st.metric("Maximum Temperature", f"{max_temp:.1f}°F")
    with col3:
        min_temp = filtered_df['Ftemp'].min()
        st.metric("Minimum Temperature", f"{min_temp:.1f}°F")

else:
    # For Monthly Averages visualization, we'll keep the controls in the sidebar
    # Year range slider
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    
    year_range = st.sidebar.slider(
        'Year Range',
        min_value=min_year,
        max_value=max_year,
        value=[min_year, max_year])
    
    # Season selection
    seasons = ['All Year', 'Winter (Dec-Feb)', 'Spring (Mar-May)', 'Summer (Jun-Aug)', 'Fall (Sep-Nov)']
    selected_season = st.sidebar.selectbox('Season', seasons)
    
    # Color scale selection
    color_scales = ['RdBu_r', 'Viridis', 'Plasma', 'Inferno', 'Turbo']
    selected_colorscale = st.sidebar.selectbox('Color Scale', color_scales)
    
    # Filter data based on year range
    filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    
    # Filter data based on season if needed
    if selected_season == 'Winter (Dec-Feb)':
        filtered_df = filtered_df[((filtered_df['month'] == 12) | (filtered_df['month'] <= 2))]
    elif selected_season == 'Spring (Mar-May)':
        filtered_df = filtered_df[(filtered_df['month'] >= 3) & (filtered_df['month'] <= 5)]
    elif selected_season == 'Summer (Jun-Aug)':
        filtered_df = filtered_df[(filtered_df['month'] >= 6) & (filtered_df['month'] <= 8)]
    elif selected_season == 'Fall (Sep-Nov)':
        filtered_df = filtered_df[(filtered_df['month'] >= 9) & (filtered_df['month'] <= 11)]
        
    st.header('Monthly Average Temperatures', divider='gray')
    
    # Compute monthly averages by year
    monthly_avg = filtered_df.groupby(['year', 'month'])['Ftemp'].mean().reset_index()

    anim_fig = px.line(
        monthly_avg,
        x="month",
        y="Ftemp",
        color=monthly_avg['year'].astype(str),  # Convert year to string
        title="Monthly Average Temperature Animation",
        labels={"month": "Month", "Ftemp": "Avg Temp (°F)", "color": "Year"},
        animation_frame='year',
        range_y=[monthly_avg['Ftemp'].min()-5, monthly_avg['Ftemp'].max()+5]
    )
    
    # Update x-axis to show month names
    anim_fig.update_xaxes(
        tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    )
    
    st.plotly_chart(anim_fig, use_container_width=True)

