import streamlit as st
import pandas as pd
from datetime import timedelta,datetime
import plotly.express as px

st.markdown("# Page 2 ❄️")

@st.cache_data
def load_data():
    data = pd.read_csv("steel_data.csv")
    data['DATE'] = pd.to_datetime(data['DATE'])
    data['NET_DIFF'] = data['HOT_TEMP'] - data['COLD_TEMP']
    return data


# Load data
df = load_data() 

with st.sidebar:
    st.title("Evonith Blast Furnace Metrics Dashboard")
    st.header("⚙️ Settings")
    
    max_date = df['DATE'].max().date()
    default_start_date = max_date - timedelta(days=365)  # Show a year by default
    default_end_date = max_date
    start_date = st.date_input("Start date", default_start_date, min_value=df['DATE'].min().date(), max_value=max_date)
    st.write(f"Selected start date: {start_date}")
    end_date = st.date_input("End date", default_end_date, min_value=df['DATE'].min().date(), max_value=max_date)
    st.write(f"Selected end date: {end_date}")
    time_frame = st.selectbox("Select time frame",
                              ("Daily", "Weekly", "Monthly", "Quarterly"),
    )

st.subheader(" Blast Furnace Metrics of Selected Parameters ")

metrics = [
    ("Total Net Temp", "NET_DIFF", '#29b5e8'),
    ("Total co2", "CO2", '#FF9F36'),
    ("Total Watch Hours", "WATCH_HOURS", '#D45B90'),
    ("Total si", "SI", '#7D44CF')
]


# Sidebar for Single and Multiple Selection
selected_option = st.sidebar.selectbox(
    "Choose an option (X-axis):",
    options=["HOT_TEMP", "COLD_TEMP", "CO2", "WATCH_HOURS", "SI", "COKE", "MN", "DIFF_TEMP"],
)

selected_values = st.sidebar.multiselect(
    "Choose options (Y-axis):",
    options=["HOT_TEMP", "COLD_TEMP", "CO2", "WATCH_HOURS", "SI", "COKE", "MN", "DIFF_TEMP"],
)



# Plot the graph if selections are valid
if selected_option and selected_values:
    # Create a Plotly line plot for each selected Y-axis value
    fig = px.line(
        data_frame=df,
        x=selected_option,
        y=selected_values,
        title=f"Graph: {selected_option} vs {', '.join(selected_values)}",
        markers=True
    )
    # Display the plot in Streamlit
    st.plotly_chart(fig)
else:
    st.write("Please select at least one X-axis option and one Y-axis option.")

