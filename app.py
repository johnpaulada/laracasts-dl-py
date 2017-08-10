import time
import re
import os
import urllib2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

driver = webdriver.Chrome()
driver.wait = WebDriverWait(driver, 10)

def open_page(link):
    driver.get(link)

def enter_credentials(username, password, username_field_id, password_field_id):
    number_field = driver.find_element_by_id(username_field_id)
    number_field.send_keys(username)

    password_field = driver.find_element_by_id(password_field_id)
    password_field.send_keys(password)

    login_form = driver.find_element_by_tag_name('form')
    login_form.submit()

def download_links(links_url):
    links = get_file_lines(links_url)

    if not os.path.exists(COURSES_DIR):
        os.mkdir(COURSES_DIR)
    os.chdir(COURSES_DIR)

    for link in links:
        download_series(link)

def download_series(link):
    try:
        open_page(link)
        series_title_element = driver.find_element_by_tag_name('h1')
        series_title = series_title_element.text

        print("Downloading {title}...".format(title = series_title))

        if not os.path.exists(series_title):
            os.mkdir(series_title)
        os.chdir(series_title)

        episode_links = driver.find_elements_by_css_selector('.episode-list-title > a')
        episodes = get_episodes(episode_links)
        download_episodes(episodes)
        os.chdir('..')
    except TimeoutException:
        os.chdir('..')
        download_series(link)

def get_episodes(episode_links):
    episodes = []

    for episode_link in episode_links:
        title = episode_link.text
        link = episode_link.get_attribute('href')
        episode = {'title': title, 'link': link}
        episodes = episodes + [episode]

    return episodes

def download_episodes(episodes):
    for episode in episodes:
        download_episode(episode)

def download_episode(episode):
    title = episode.get('title')
    link = episode.get('link')
    print("  Downloading {title}...".format(title = title))
    open_page(link)
    download_link = driver.find_element_by_tag_name('video')
    video_url = download_link.get_attribute('src')
    save_video(title, video_url)

def save_video(video_title, video_url):
    video_file = urllib2.urlopen(video_url)
    video_data = video_file.read()
    video_filename = video_title + ".mp4"
    if not os.path.exists(video_filename):
        with open(video_filename, "wb") as file_writer:
            file_writer.write(video_data)

def get_file_lines(url):
    lines = []

    for line in open(url):
        if line != '':
            lines = lines + [line]

    return lines

LOGIN_URL = 'https://laracasts.com/login'
USERNAME_FIELD_ID = "email"
PASSWORD_FIELD_ID = "password"
LINKS_URL = "links.txt"
COURSES_DIR = 'courses'
USERNAME_INDEX = 0
PASSWORD_INDEX = 1
CREDENTIALS = get_file_lines('credentials')
USERNAME = CREDENTIALS[USERNAME_INDEX]
PASSWORD = CREDENTIALS[PASSWORD_INDEX]

open_page(LOGIN_URL)
enter_credentials(USERNAME, PASSWORD, USERNAME_FIELD_ID, PASSWORD_FIELD_ID)
download_links(LINKS_URL)