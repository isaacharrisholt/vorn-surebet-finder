import time
import platform
import os

from .. import utils

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, SessionNotCreatedException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

SITE_LINK = 'https://sports.bwin.com/en/sports/live/all'


# Initialises the webdriver for use
def initialise_webdriver():
    # Initialise webdriver options
    options = Options()
    options.headless = True
    options.add_argument('window-size=1920,1080')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Path to Chromedriver
    if platform.system() == 'Windows':
        path = 'chromedriver/chromedriver.exe'
    elif platform.system() == 'Darwin':
        path = 'chromedriver/chromedriver_mac'
        os.chmod(path, 755)
    else:
        path = 'chromedriver/chromedriver_linux'
        os.chmod(path, 755)

    # Initialise and return webdriver
    try:
        driver = webdriver.Chrome(path, options=options)
    except SessionNotCreatedException:
        utils.pinput('Please update your version of Google Chrome. If it\'s up to date and still not working, please '
                     'message me on GitHub.\nPress Enter to quit.')
        utils.quit_program()
    return driver


# Reduces change of popup
def prevent_popup(driver):
    # Find promo banner
    promo_banner = WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.CLASS_NAME,
                                                                                  'header-top-promo-banner')))
    try:
        close_button = WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.CLASS_NAME, 'theme-close-i')))
        close_button.click()
    except (StaleElementReferenceException, TimeoutException):
        print('-- bwin: Couldn\'t find promo banner close button.')


# Accepts cookies on site
def accept_cookies(driver):
    accept = WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.XPATH,
                                                                         '//*[@id="onetrust-accept-btn-handler"]')))
    accept.click()


# Selects desired sport from options
def select_sport(driver, sport):
    sport_selector = driver.find_element_by_class_name('list-card')

    # Get the buttons
    sport_selector_buttons = sport_selector.find_elements_by_class_name('list-item')

    # Iterate through buttons and check if text matches
    for button in sport_selector_buttons:
        text_field = button.find_element_by_class_name('title')
        if text_field.text == sport:
            button.click()
            return True

    return False


# Expands listings to show all live games
def expand_listings(driver):
    expanded_url = driver.current_url + '?fallback=false'
    driver.get(expanded_url)

    # Check to see if page has loaded
    for i in range(5):
        try:
            WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.CLASS_NAME, 'grid-group-container')))
            return True
        except TimeoutException:
            print(f'-- bwin: Page took too long to load ({i}) time(s).')
    return False


# Changes market dropdown
def change_market(driver, market):
    # Get dropdown and click it
    dropdowns = WebDriverWait(driver, 5).until(ec.presence_of_all_elements_located((By.TAG_NAME, 'ms-group-selector')))
    dropdown = WebDriverWait(dropdowns[0], 10).until(ec.element_to_be_clickable((By.XPATH, './/ms-dropdown')))
    driver.execute_script('arguments[0].click()', dropdown)

    # Find dropdown menu and get the options
    selector = driver.find_element_by_class_name('select')
    options = selector.find_elements_by_class_name('option')

    for option in options:
        option_text = option.get_attribute('innerHTML').replace('<!---->', '').strip()
        if option_text == market:
            driver.execute_script('arguments[0].click()', option)
            return True

    return False


# Gets the odds for current market
def get_market_odds(driver, market, odds_dict):
    odds_list = []
    competitors = []
    time.sleep(1)

    # Box containing events
    box = driver.find_element_by_xpath('//ms-grid[contains(@sortingtracking,"Live")]')

    # Get single row events
    rows = WebDriverWait(box, 5).until(ec.presence_of_all_elements_located((By.CLASS_NAME, 'grid-event')))

    # Iterate rows and find odds and competitor names
    for row in rows:
        try:
            odds = row.find_elements_by_class_name('grid-option-group')

            # Remove empty odds
            try:
                empty_events = row.find_elements_by_class_name('empty')
                odds = [odd for odd in odds if odd not in empty_events]
            except Exception:
                pass

            # Return if odds is empty
            if not odds:
                continue

            # We only want the first dropdown, so use odds[0]
            odd = odds[0]

            # If looking at Over/Under X goals, we only want odds where we have X goals
            if 'Over/Under' in market:
                goals = market.split(' ')[1]

                if goals not in odd.text:
                    continue
                else:
                    odds_list.append(odd.text.replace(goals, '').strip('\n'))
            else:
                odds_list.append(odd.text)

            # Get competitor names
            competitor_name_fields = row.find_elements_by_class_name('participant')
            competitor_names = [competitor_name.text for competitor_name in competitor_name_fields]
            competitors.append(' - '.join(competitor_names))
        except StaleElementReferenceException:
            continue

    # Store data in odds dictionary and return
    odds_dict[market] = {}
    odds_dict[market]['Odds'] = odds_list
    odds_dict[market]['Competitors'] = competitors
    print(f'-- bwin: Got odds for {market}')
    return odds_dict


# Get all odds for all specified markets
def get_all_odds(driver, markets):
    odds_dict = {}

    # Check that markets is not empty
    if len(markets) > 1:
        print('-- bwin: Getting multi-market odds')
        for market in markets:
            # bwin doesn't have separate markets for Over/Under X Goals, so deal with it this way
            if 'Over/Under' in market:
                market_to_change = 'Over/Under'
            else:
                market_to_change = market

            if not change_market(driver, market_to_change):
                print(f'-- bwin: "{market}" market not available')
                odds_dict[market] = {}
                odds_dict[market]['Odds'] = []
                odds_dict[market]['Competitors'] = []
                continue
            odds_dict = get_market_odds(driver, market, odds_dict)
    elif not markets:
        print('-- bwin: Getting match odds')
        odds_dict = get_market_odds(driver, 'win', odds_dict)
    else:
        print('-- bwin: Getting single market odds')
        if not change_market(driver, markets[0]):
            print(f'-- bwin: "{markets[0]}" market not available')
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

    # Open page, prevent popup and accept cookies if it appears
    driver.get(SITE_LINK)
    prevent_popup(driver)

    try:
        accept_cookies(driver)
    except TimeoutException:
        pass

    # Select relevant sport from list and return availability
    sport_available = select_sport(driver, sport)

    # If sport not available, log message and return empty dictionary
    if not sport_available:
        print(f'- bwin: No live {sport.lower()} available right now.')
        queue.put({})
        return

    # Get all the odds
    try:
        odds_dict = get_all_odds(driver, markets)
    except TimeoutException:
        print(f'- bwin: Timed out, returning.')
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
        final_data = {'bwin': final_df}
        queue.put(final_data)
        print('- bwin: Returned odds')
        return
    except:
        print('- bwin: No data gathered')
        queue.put({})
        return
