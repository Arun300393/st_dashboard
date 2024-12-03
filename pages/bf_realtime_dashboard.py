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
from dotenv import load_dotenv


load_dotenv()
# Set up WebDriver
service = Service(ChromeDriverManager().install())

download_dir = r'C:\Users\princ\Downloads\evonith_plant_data\\'

# Configure Chrome options
options  = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
prefs = {'profile.default_content_settings.popups': False,
    'download.default_directory' : download_dir,
    'directory_upgrade': True}
options.add_experimental_option('prefs', prefs)
chrome_options = Options()
driver = webdriver.Chrome(options=options)

#Open the webpage
USERNAME = os.getenv("USERNAME_REALTIMEDATA")
PASSWORD = os.getenv("PASSWORD_REALTIMEDATA")
driver.get("https://mcartalert.com/WebService/GeneralService.asmx?op=realtimedataVP")


def download_csv():
    """
    Automates the CSV download by clicking the download button.
    """
    try:
    # Locate the input fields by ID (or another appropriate locator) and giving Creds.
    # Locate and click the download button
        username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "user"))
        )
        username_input.send_keys(USERNAME)
        password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys(PASSWORD)
        download_button = driver.find_element(By.CLASS_NAME, "button")  # Replace with correct locator
        download_button.click()
        time.sleep(2)
        main_window = driver.current_window_handle
        all_windows = driver.window_handles
        for window in all_windows:
            if window != main_window:
                driver.switch_to.window(window)
                driver.close()
            driver.switch_to.window(main_window)

        username_input = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.NAME, "user"))
        )
        username_input.clear()
        password_input = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.clear()

    except Exception as e:
        st.error(f"Error downloading file: {e}")


# Streamlit configuration
st.title("Real-Time Data Dashboard")
st.subheader("Live CSV Updates")

if 'dataframe' not in st.session_state:
    st.session_state.dataframe = pd.DataFrame()
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
    #TODO: Delete read csv files.
    return pd.read_csv(os.path.join(download_dir, latest_file))

def data_validator(data: pd.DataFrame) -> pd.DataFrame:
    return data

def copy_to_db():
    return None

def update_dashboard(olddata: pd.DataFrame=None):
    """
    Periodically fetch and display the latest CSV data.
    """
    download_csv()  # Trigger CSV download
    
    # Load the latest CSV data
    newdata = read_latest_csv()
    copy_to_db(newdata)
    data_validator(newdata)

    if olddata is not None:
        if len(olddata) != 0:
            data = pd.concat([olddata, newdata])
        else:
            data = newdata
    else:
        data = newdata
    #TODO: Index of the dataframe should dhave date and time 
    with placeholder.container():
        st.write("Last Updated:", time.strftime("%Y-%m-%d %H:%M:%S"))
        st.dataframe(data.tail(100))  # Display the DataFrame
        
        # Example plot
        st.line_chart(data.select_dtypes(include=['float', 'int']))
    return data

def flush(data):
    #TODO: Save the dataframe as csv file.
    pass

# Run the dashboard
if st.button("Start Dashboard"):
    while True:
        if len(st.session_state.dataframe) >= 100000:
            flush(st.session_state.dataframe)
            st.session_state.dataframe = pd.Dataframe()
        if len(st.session_state.dataframe) == 0:
            st.session_state.dataframe = update_dashboard()
        else:
            st.session_state.dataframe = update_dashboard(st.session_state.dataframe)
