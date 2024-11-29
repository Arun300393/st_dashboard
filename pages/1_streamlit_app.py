import streamlit as st
import pandas as pd
from datetime import timedelta, datetime


print(file_path)

# Set page config
st.set_page_config(page_title="Evonith Blast Furnace", layout="wide")

@st.cache_data
def load_data():
    data = pd.read_csv("steel_data.csv")
    data['DATE'] = pd.to_datetime(data['DATE'])
    data['NET_DIFF'] = data['HOT_TEMP'] - data['COLD_TEMP']
    return data

def custom_quarter(date):
    month = date.month
    print(month)
    year = date.year
    if month in [2, 3, 4]:
        return pd.Period(year=year, quarter=1, freq='Q')
    elif month in [5, 6, 7]:
        return pd.Period(year=year, quarter=2, freq='Q')
    elif month in [8, 9, 10]:
        return pd.Period(year=year, quarter=3, freq='Q')
    else:  # month in [11, 12, 1]
        return pd.Period(year=year if month != 1 else year-1, quarter=4, freq='Q')
    
def aggregate_data(df, freq):
    if freq == 'Q':
        df = df.copy()
        df['CUSTOM_Q'] = df['DATE'].apply(custom_quarter)
        df_agg = df.groupby('CUSTOM_Q').agg({
            'CO2': 'sum',
            'WATCH_HOURS': 'sum',
            'NET_DIFF': 'sum',
            'SI': 'sum',
            'MN': 'sum',
            'COKE': 'sum',
        })
        return df_agg
    else:
        return df.resample(freq, on='DATE').agg({
            'CO2': 'sum',
            'WATCH_HOURS': 'sum',
            'NET_DIFF': 'sum',
            'SI': 'sum',
            'MN': 'sum',
            'COKE': 'sum',
        })

def get_weekly_data(df):
    return aggregate_data(df, 'W-MON')

def get_monthly_data(df):
    return aggregate_data(df, 'M')

def get_quarterly_data(df):
    return aggregate_data(df, 'Q')

def format_with_commas(number):
    return f"{number:,}"

def create_metric_chart(df, column, color, chart_type, height=150, time_frame='Daily'):
    chart_data = df[[column]].copy()
    if time_frame == 'Quarterly':
        chart_data.index = chart_data.index.strftime('%Y Q%q ')
    if chart_type=='Bar':
        st.bar_chart(chart_data, y=column, color=color, height=height)
    if chart_type=='Area':
        st.area_chart(chart_data, y=column, color=color, height=height)

def is_period_complete(date, freq):
    today = datetime.now()
    if freq == 'D':
        return date.date() < today.date()
    elif freq == 'W':
        return date + timedelta(days=6) < today
    elif freq == 'M':
        next_month = date.replace(day=28) + timedelta(days=4)
        return next_month.replace(day=1) <= today
    elif freq == 'Q':
        current_quarter = custom_quarter(today)
        return date < current_quarter

def calculate_delta(df, column):
    if len(df) < 2:
        return 0, 0
    current_value = df[column].iloc[-1]
    previous_value = df[column].iloc[-2]
    delta = current_value - previous_value
    delta_percent = (delta / previous_value) * 100 if previous_value != 0 else 0
    return delta, delta_percent

def display_metric(col, title, value, df, column, color, time_frame):
    with col:
        with st.container(border=True):
            delta, delta_percent = calculate_delta(df, column)
            delta_str = f"{delta:+,.0f} ({delta_percent:+.2f}%)"
            st.metric(title, format_with_commas(value), delta=delta_str)
            create_metric_chart(df, column, color, time_frame=time_frame, chart_type=chart_selection)
            
            last_period = df.index[-1]
            freq = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M', 'Quarterly': 'Q'}[time_frame]
            if not is_period_complete(last_period, freq):
                st.caption(f"Note: The last {time_frame.lower()[:-2] if time_frame != 'Daily' else 'day'} is incomplete.")

# Load data
df = load_data()

# Set up input widgets
st.logo(image="images/evonith_logo.png")

df_cumulative = df.copy()
for column in ['NET_DIFF', 'CO2', 'WATCH_HOURS', 'SI']:
    df_cumulative[column] = df_cumulative[column].cumsum()

with st.sidebar:
    st.title("Evonith Blast Furnace Metrics Dashboard")
    st.header("⚙️ Settings")
    
    max_date = df['DATE'].max().date()
    default_start_date = max_date - timedelta(days=365)  # Show a year by default
    default_end_date = max_date
    start_date = st.date_input("Start date", default_start_date, min_value=df['DATE'].min().date(), max_value=max_date)
    end_date = st.date_input("End date", default_end_date, min_value=df['DATE'].min().date(), max_value=max_date)
    time_frame = st.selectbox("Select time frame",
                              ("Daily", "Weekly", "Monthly", "Quarterly"),
    )
    chart_selection = st.selectbox("Select a chart type",
                                   ("Bar", "Area"))
    
# Prepare data based on selected time frame
if time_frame == 'Daily':
    df_display = df.set_index('DATE')
elif time_frame == 'Weekly':
    df_display = get_weekly_data(df)
elif time_frame == 'Monthly':
    df_display = get_monthly_data(df)
elif time_frame == 'Quarterly':
    df_display = get_quarterly_data(df)

# Display Key Metrics
st.subheader(" Blast Furnace Metrics of Selected Parameters ")

metrics = [
    ("Total Net Temp", "NET_DIFF", '#29b5e8'),
    ("Total co2", "CO2", '#FF9F36'),
    ("Total Watch Hours", "WATCH_HOURS", '#D45B90'),
    ("Total si", "SI", '#7D44CF')
]

# Stream page columns count
cols = st.columns(4) 
for col, (title, column, color) in zip(cols, metrics):
    total_value = df[column].sum()
    display_metric(col, title, total_value, df_display, column, color, time_frame)

st.subheader("Selected Duration")

if time_frame == 'Quarterly':
    start_quarter = custom_quarter(start_date)
    end_quarter = custom_quarter(end_date)
    mask = (df_display.index >= start_quarter) & (df_display.index <= end_quarter)
else:
    mask = (df_display.index >= pd.Timestamp(start_date)) & (df_display.index <= pd.Timestamp(end_date))
df_filtered = df_display.loc[mask]

cols = st.columns(4)
for col, (title, column, color) in zip(cols, metrics):
    display_metric(col, title.split()[-1], df_filtered[column].sum(), df_filtered, column, color, time_frame)

# DataFrame display
with st.expander('See DataFrame (Selected time frame)'):
    st.dataframe(df_filtered)

# Sidebar form with options
with st.sidebar.form(key="Operator Details"):
    st.sidebar.header("Operator Details")
    
    # Dropdown menu with options
    options = [
        "HOT_TEMP", 
        "COLD_TEMP", 
        "CO2", 
        "WATCH_HOURS", 
        "SI", 
        "COKE", 
        "MN", 
        "DIFF_TEMP"
    ]
    
    selected_option = st.selectbox("Select an option:", options)
    
    # Submit button for the form
    submit_button = st.form_submit_button(label="Submit")

# Display the selected option
if submit_button:
    st.write(f"You selected: {selected_option}")