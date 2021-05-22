import time
import platform
import os

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

SITE_LINK = 'https://sports.ladbrokes.com/in-play/football'


# Initialises the webdriver for use
def initialise_webdriver():
    # Initialise webdriver options
    options = Options()
    options.headless = True
    options.add_argument('window-size=1920x1080')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Path to chromedriver
    if platform.system() == 'Windows':
        path = 'chromedriver/chromedriver.exe'
    elif platform.system() == 'Darwin':
        options.add_argument('--no-sandbox')
        os.chmod('chromedriver/chromedriver_mac', 755)
        path = 'chromedriver/chromedriver_mac'
    else:
        options.add_argument('--no-sandbox')
        os.chmod('chromedriver/chromedriver_linux', 755)
        path = 'chromedriver/chromedriver_linux'

    # Initialise and return webdriver
    driver = webdriver.Chrome(path, options=options)
    return driver


# Accepts cookies on site
def accept_cookies(driver):
    cookie_msg = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME,
                                                                                 'cookie-consent-message')))
    accept = WebDriverWait(cookie_msg, 15).until(ec.element_to_be_clickable((By.CLASS_NAME, 'btn-success')))
    accept.click()


# Selects desired sport from options
def select_sport(driver, sport):
    sport_selector = driver.find_element_by_class_name('left-menu-items')

    # Get the buttons
    sport_selector_buttons = sport_selector.find_elements_by_class_name('left-menu-item')

    # Iterate through buttons and click if text matches
    for button in sport_selector_buttons:
        if button.text == sport:
            button.click()

            # Find and click 'In-Play' label
            switch_buttons = WebDriverWait(driver, 5).until(ec.visibility_of_all_elements_located((By.CLASS_NAME,
                                                                                                   'switch-btn')))
            for switch_button in switch_buttons:
                if switch_button.text.lower() == 'in-play':
                    switch_button.click()
                    break

            return True

    return False


# Expand listing to show all live games
def expand_listings(driver):
    # Get all listings that aren't expanded
    WebDriverWait(driver, 5).until(ec.visibility_of_any_elements_located((By.CLASS_NAME, 'accordion-header')))
    listings = driver.find_elements_by_xpath('//accordion[position()>2]/header')

    # Iterate through listings and open them
    for listing in listings:
        driver.execute_script('arguments[0].click();', listing)
        # Only uncomment this if you get errors
        # time.sleep(0.5)


# Changes market dropdown
def change_market(driver, market):
    dropdown_list = WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.CLASS_NAME, 'dropdown-menu')))
    dropdown_items = dropdown_list.find_elements_by_xpath('//*[contains(@data-crlat, "dropdown.menuTitle")]')

    for item in dropdown_items:
        if item.get_attribute("innerHTML") == market:
            driver.execute_script('arguments[0].click();', item)
            time.sleep(1)

            # Expand listings
            while True:
                try:
                    expand_listings(driver)
                    break
                except StaleElementReferenceException:
                    pass

            return True

    return False


# Gets odds for current market
def get_market_odds(driver, market, odds_dict):
    odds_list = []
    competitors = []
    time.sleep(1)

    # Box containing events
    section = driver.find_element_by_xpath('//*[contains(@data-crlat, "accordionsList")]')
    box = section.find_element_by_tag_name('div')

    # Get single row events
    rows = box.find_elements_by_class_name('sport-card')

    # Iterate through rows and find odds and competitor names
    for row in rows:
        try:
            odds = row.find_element_by_class_name('sport-card-btn-content')
            competitor_names = row.find_element_by_class_name('sport-card-names').text
        except StaleElementReferenceException:
            continue
        odds_list.append(odds.text)
        competitors.append(competitor_names.replace('\n', ' - '))

    # Store data in odds dictionary and return
    # Store data in odds dictionary and return
    odds_dict[market] = {}
    odds_dict[market]['Odds'] = odds_list
    odds_dict[market]['Competitors'] = competitors
    print(f'-- Ladbrokes: Got odds for {market}')
    return odds_dict


def get_all_odds(driver, markets):
    odds_dict = {}

    # Check that markets is not empty
    if len(markets) > 1:
        print('-- Ladbrokes: Getting multi-market odds')
        for market in markets:
            if not change_market(driver, market):
                print(f'-- Ladbrokes: "{market}" market not available')
                continue
            get_market_odds(driver, market, odds_dict)
    elif not markets:
        print('-- Ladbrokes: Getting match odds')
        odds_dict = get_market_odds(driver, 'win', odds_dict)
    else:
        print('-- Ladbrokes: Getting single market odds')
        if not change_market(driver, markets[0]):
            print(f'-- Ladbrokes: "{markets[0]}" market not available')
        else:
            odds_dict = get_market_odds(driver, markets[0], odds_dict)

    return odds_dict


# Create dataframe from odds
def create_df(odds_dict):
    df_list = []

    # Create dataframes from odds dictionary
    for market in odds_dict:
        df = pd.DataFrame(odds_dict[market]).set_index('Competitors')
        df.rename(columns={'Odds': market}, inplace=True)
        df_list.append(df)

    # Concatenate dataframes and clean
    final_df = pd.concat(df_list, axis=1, sort=True)

    final_df.reset_index(inplace=True)
    final_df.rename(columns={'index': 'Competitors'}, inplace=True)

    final_df = final_df.fillna('').replace('SUSP', '1', regex=True).replace('CLOSED', '1', regex=True) \
        .replace('EVS', '1', regex=True)
    final_df = final_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    return final_df


# Main function
def get_data(queue, sport, markets=None):
    if markets is None:
        markets = []

    # Initialise the webdriver
    driver = initialise_webdriver()

    # Open page and accept cookies
    driver.get(SITE_LINK)

    try:
        accept_cookies(driver)
    except TimeoutException:
        pass

    # Select relevant sport from list and return availability
    sport_available = select_sport(driver, sport)

    # If sport not available, log message and return empty dictionary
    if not sport_available:
        print(f'- Ladbrokes: No live {sport.lower()} available right now.')
        queue.put({})
        return

    # Get all the odds
    try:
        odds_dict = get_all_odds(driver, markets)
    except TimeoutError:
        print(f'- Ladbrokes: Timed out, returning.')
        queue.put({})
        return

    # Finished with the driver. It can sleep now
    driver.quit()

    # Set pandas options
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    try:
        # Create a dataframe from all odds data and store in dictionary to preserve name
        final_df = create_df(odds_dict)
        final_data = {'Ladbrokes': final_df}
        queue.put(final_data)
        print('- Ladbrokes: Returned odds')
        return
    except:
        print('- Ladbrokes: No data gathered')
        queue.put({})
        return
