from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pandas as pd
import streamlit as st

# Set up WebDriver
service = Service(ChromeDriverManager().install())

download_dir = r'C:\Users\princ\Downloads\evonith_plant_data\\'
# Configure Chrome options
options  = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
prefs = {'profile.default_content_settings.popups': 0,
    'download.default_directory' : download_dir,
    'directory_upgrade': True}
options.add_experimental_option('prefs', prefs)

driver = webdriver.Chrome(options=options)

# Open the webpage
driver.get("https://mcartalert.com/WebService/GeneralService.asmx?op=realtimedataVP")

def download_csv():
    """
    Automates the CSV download by clicking the download button.
    """
    try:
        # Locate the input fields by ID (or another appropriate locator) and giving Creds.
        # Locate and click the download button
        input_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "user"))
        )
        input_field.send_keys("REALTIMEDATASERVICE")
        input_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
        )
        input_field.send_keys("283ALERT2024")
        download_button = driver.find_element(By.CLASS_NAME, "button")  # Replace with correct locator
        download_button.click()
    except Exception as e:
        st.error(f"Error downloading file: {e}")


# Streamlit configuration
st.title("Real-Time Data Dashboard")
st.subheader("Live CSV Updates")

# Placeholder for plots
placeholder = st.empty()

def read_latest_csv():
    """
    Reads the latest CSV file from the download directory.
    """
    files = [f for f in os.listdir(download_dir) if f.endswith('.csv')]
    if not files:
        return None
    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(download_dir, x)))
    return pd.read_csv(os.path.join(download_dir, latest_file))

def update_dashboard():
    """
    Periodically fetch and display the latest CSV data.
    """
    while True:
        download_csv()  # Trigger CSV download
        time.sleep(60)  # Wait for 1 minute before the next download
        
        # Load the latest CSV data
        data = read_latest_csv()
        if data is not None:
            with placeholder.container():
                st.write("Last Updated:", time.strftime("%Y-%m-%d %H:%M:%S"))
                st.dataframe(data)  # Display the DataFrame
                
                # Example plot
                st.line_chart(data.select_dtypes(include=['float', 'int']))
        else:
            st.warning("No CSV files found. Waiting for the first download...")

# Run the dashboard
if st.button("Start Dashboard"):
    update_dashboard()
