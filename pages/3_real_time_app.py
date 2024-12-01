from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import pandas as pd
from io import StringIO
import time
import streamlit as st

# Setup Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service = service)

# Define the API endpoint
API_URL = "https://mcartalert.com/WebService/GeneralService.asmx?op=realtimedataVP"

# Streamlit Configuration
st.set_page_config(page_title="Real-Time Dashboard", layout="wide")

st.title("Real-Time Data Dashboard")

# Placeholder for dynamic updates
placeholder = st.empty()

def download_csv_data(url):
    """
    download CSV data from the API and return a Pandas DataFrame.
    """
    response = requests.get(url)
    if response.status_code == 200:
        # Convert CSV data to a Pandas DataFrame
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        return df
    else:
        st.error(f"Failed to download data: {response.status_code}")
        return None

def update_dashboard():
    """
    download data periodically and update the dashboard.
    """
    while True:
        data = download_csv_data(API_URL)
        if data is not None:
            with placeholder.container():
                st.write("Last Updated:", time.strftime("%Y-%m-%d %H:%M:%S"))
                st.dataframe(data)  # Display the DataFrame as a table
        time.sleep(60)  # Wait for 1 minute before downloading data again

# Run the dashboard
if st.button("Start Live Dashboard"):
    update_dashboard()
