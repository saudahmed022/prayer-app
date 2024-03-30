from datetime import datetime
from selenium import webdriver
import pandas as pd
from tkinter import *
import pygame
from PIL import Image, ImageTk

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

site = 'https://www.muslimsocietyinc.org/'

# Function to update prayer_dict from the website
def update_prayer_dict():
    wd = webdriver.Chrome(options=options)
    wd.get(site)
    html = wd.page_source
    df = pd.read_html(html)

    # Extract the 2nd and 3rd columns (index 1 and 2)
    selected_data = df[0].iloc[:, [1, 2]]

    # Rename the DataFrame columns for clarity
    selected_data = selected_data.drop(columns=[2])
    selected_data = selected_data.drop([0, 1])
    prayers = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
    selected_data[0] = prayers
    updated_prayer_dict = selected_data.set_index(0).to_dict()[1]

    wd.quit()  # Close the WebDriver
    print('Successfully Updated!')
    return updated_prayer_dict

# Function to play the alarm sound
def play_alarm(sound_file):
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play(0)
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)   

# Function to convert time from 12-hour format to 24-hour format
def convert_to_24_hour_format(time_str):
    return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")

# Function to check for prayer times and alarms
def update_time(prayer_dict):
    current_time = datetime.now().strftime("%H:%M")  # Get the current time in 24-hour format
    time_label.config(text=datetime.now().strftime("%I:%M %p"))  # Update the time label

    # Find the next prayer and its time
    next_prayer = None
    for prayer, time_str in prayer_dict.items():
        prayer_time = convert_to_24_hour_format(time_str)
        if current_time < prayer_time:
            next_prayer = (prayer, time_str)  # Use 12-hour format time here
            break

    if next_prayer:
        prayer_name, prayer_time = next_prayer
        next_prayer_label.config(text=f"Next Prayer: {prayer_name} at {prayer_time}")
    else:
        # All prayers for the day are completed, reset to Fajr
        next_prayer_label.config(text="Next Prayer: Fajr at " + convert_to_24_hour_format(prayer_dict['Fajr']) + " AM")

    # Check for alarms
    for prayer, time_str in prayer_dict.items():
        prayer_time = convert_to_24_hour_format(time_str)
        if current_time == prayer_time:
            # Trigger an alarm for the current prayer
            if prayer == "Fajr":
                azan_file = "fajr_azan.mp3"
            else:
                azan_file = "azan.mp3"
            play_alarm(azan_file)
            print(f"It's time for {prayer}!")
    
def update_date():
    current_date_label.config(text=datetime.now().strftime("%A, %B %d, %Y"))
    root.after(1000 * 60 * 60, update_date)  # Update the date every hour (3600000 milliseconds)

# Function to update the time and schedule the next update
def update_time_and_schedule():
    update_time(prayer_dict)
    root.after(1000, update_time_and_schedule)

def check_and_update_prayer_dict():
    current_time = datetime.now().strftime("%H:%M:%S")
    # Check if the current time is 3:00:01 AM or 3:00:02 AM
    if current_time == "03:00:01" or current_time == "03:00:02":
        global prayer_dict
        prayer_dict = update_prayer_dict()
        print("Prayers updated at 3:00:01 AM or 3:00:02 AM")
    root.after(1000, check_and_update_prayer_dict)

# Create the main window
root = Tk()
root.title("Prayer Times and Alarms")
root.geometry('800x500')

prayer_dict = update_prayer_dict()

# Create a label for displaying the current time
time_label = Label(root, text="")
time_label.configure(font='Helvetica 68 bold')
time_label.pack(pady=10)

# Create a label for displaying the next prayer
next_prayer_label = Label(root, text="")
next_prayer_label.configure(font='Helvetica 28 bold')
next_prayer_label.pack(pady=10)

# Create a label for displaying the current date
current_date_label = Label(root, text="")
current_date_label.configure(font='Helvetica 28 bold')
current_date_label.pack(pady=10)

# Load and display an image using Pillow (PIL)
image_path = "image-1.png"  # Replace with the path to your image file
image = Image.open(image_path)
image = ImageTk.PhotoImage(image)
image_label = Label(root, image=image)
image_label.pack()  # Place the image label on the right side

# Schedule the check_and_update_prayer_dict function to run every second
check_and_update_prayer_dict()

# Start updating the time and checking for alarms
update_time_and_schedule()

# Start updating the datea
update_date()

# Run the Tkinter main loop
root.mainloop()