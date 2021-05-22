import time
import platform
import os

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

SITE_LINK = 'https://www.betfair.com/sport/inplay'


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


# Clicks the accept cookies popup
def accept_cookies(driver):
    time.sleep(2)
    accept = driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]')
    accept.click()


# Selects the desired sport from the row
def select_sport(driver, sport):
    sport_selector = driver.find_element_by_class_name('ip-sports-selector')

    # Find right arrow for if sport isn't visible
    right_arrow = sport_selector.find_element_by_class_name('arrow-right')
    tries = 0
    while True:
        sport_selector_buttons = WebDriverWait(sport_selector, 5).until(
            ec.visibility_of_all_elements_located((By.CLASS_NAME, 'ip-button')))
        for button in sport_selector_buttons:
            # Checks if button text matches desired sport
            text_field = button.find_element_by_xpath('.//*[@class="ip-sport-name"]')
            if text_field.text == sport:
                button.click()
                return True
        try:
            # Clicks arrow if sport wasn't visible
            right_arrow.click()
        except Exception:
            pass

        # If the right arrow has been disabled, and has been tried multiple times, return False
        if 'disabled' in right_arrow.get_attribute('class'):
            tries += 1
            if tries == 2:
                return False


# Changes market dropdown
def change_market(driver, market):
    dropdown = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.CLASS_NAME, 'com-dropdown-header')))
    dropdown.click()
    try:
        market_choice = WebDriverWait(dropdown, 5).until(
            ec.element_to_be_clickable((By.XPATH, f'//*[contains(text(), "{market}")]')))
    except Exception:
        return False
    market_choice.click()
    return True


# Gets odds for current market
def get_market_odds(driver, market, odds_dict):
    odds_list = []
    competitors = []
    time.sleep(1)

    # Box containing events
    box = driver.find_element_by_xpath('//div[contains(@class, "sport-container") and contains(@class, "visible")]')

    # Get single row events
    rows = WebDriverWait(box, 10).until(ec.visibility_of_all_elements_located((By.CLASS_NAME, 'com-coupon-line')))

    # Iterate through rows and find odds and competitor names
    for row in rows:
        odds = row.find_element_by_xpath('.//div[contains(@class, "runner-list")]')
        odds_list.append(odds.text)
        home = row.find_element_by_class_name('home-team-name').text
        away = row.find_element_by_class_name('away-team-name').text
        competitors.append(home + ' - ' + away)

    # Store data in odds dictionary and return
    odds_dict[market] = {}
    odds_dict[market]['Odds'] = odds_list
    odds_dict[market]['Competitors'] = competitors
    print(f'-- Betfair: Got odds for {market}')
    return odds_dict


# Get all odds for all specified markets
def get_all_odds(driver, markets):
    odds_dict = {}

    # Check that markets is not empty
    if len(markets) > 1:
        print('-- Betfair: Getting multi-market odds')
        for market in markets:
            if not change_market(driver, market):
                print(f'-- Betfair: "{market}" market not available')
                continue
            odds_dict = get_market_odds(driver, market, odds_dict)
    elif not markets:
        print('-- Betfair: Getting match odds')
        odds_dict = get_market_odds(driver, 'win', odds_dict)
    else:
        print('-- Betfair: Getting single market odds')
        if not change_market(driver, markets[0]):
            print(f'-- Betfair: "{markets[0]}" market not available')
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

    final_df = final_df.fillna('').replace('SUSPENDED', '1', regex=True).replace('CLOSED', '1', regex=True) \
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
    accept_cookies(driver)

    # Select relevant sport from list and return availability
    sport_available = select_sport(driver, sport)

    # If sport not available, log message and return empty dictionary
    if not sport_available:
        print(f'- Betfair: No live {sport.lower()} available right now.')
        queue.put({})
        return

    # Get all the odds
    try:
        odds_dict = get_all_odds(driver, markets)
    except TimeoutError:
        print(f'- Betfair: Timed out, returning.')
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
        final_data = {'Betfair': final_df}
        queue.put(final_data)
        print('- Betfair: Returned odds')
        return
    except:
        print('- Betfair: No data gathered')
        queue.put({})
        return
