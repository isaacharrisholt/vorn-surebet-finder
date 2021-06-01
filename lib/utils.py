# Utility functions
import json
import os
import sys
import re

colours_installed = True

try:
    from colorama import Fore, Style
except ModuleNotFoundError:
    colours_installed = False

if colours_installed:
    colours = {"RED": Fore.LIGHTRED_EX, "GREEN": Fore.GREEN, "YELLOW": Fore.LIGHTYELLOW_EX, "RESET": Fore.RESET}
else:
    colours = {"RED": "", "GREEN": "", "YELLOW": "", "RESET": ""}

LINE = "------------------------------------------------------------------------------------------------------------" \
       "-------"


# Rounds a number to the nearest whole value multiple of 'base'
def round_to(x, base=5):
    return base * round(x / base)


# Damned Europeans...
def replace_comma(x):
    if isinstance(x, str):
        x = re.sub(r'\d,\d', '1', x)
    return x


# Converts fractional odds to floats, bearing in mind float odds show full return, whereas fractional odds ignore
# initial stake
def convert_odds(x):
    if isinstance(x, str) and '/' in x:
        numerator = float(x.split('/')[0])
        denominator = float(x.split('/')[1])
        x = float(numerator / denominator + 1)
    return float(x)


# Checks length of odds
def check_length(x, num):
    if len(x.split('\n')) != num:
        x = ('1\n' * num).strip('\n')
    return x


# Clears the terminal
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# Translates standard market names to individual site market names
def translate_to_site_market(market, broker):
    with open('files/market_translations.json') as market_translations:
        translations = json.load(market_translations)

    try:
        return translations[broker][market]
    except KeyError:
        return market


# Translates site market names to standard market names
def translate_to_standard_market(market, broker):
    with open('files/market_translations.json') as market_translations:
        translations = json.load(market_translations)
    translations = {translations[broker][key]: key for key in translations[broker]}

    try:
        return translations[broker][market]
    except KeyError:
        return market


# Translates column names to standard market names for program
def translate_columns(df, broker):
    with open('files/market_translations.json') as market_translations:
        translations = json.load(market_translations)

    # Have to reverse dictionary for pandas rename
    broker_translations = {translations[broker][key]: key for key in translations[broker]}

    renamed = df.rename(columns=broker_translations)
    return renamed


# Pretty print
def pprint(string):
    formatted_string = string.format(**colours)
    print(f"\n{LINE}")
    print(formatted_string)
    print(f"{LINE}\n")


# Pretty input
def pinput(string):
    formatted_string = string.format(**colours)
    print(f"\n{LINE}")
    print(formatted_string)
    return input(f"{LINE}\n: ")


# Quits the program
def quit_program():
    clear()
    pinput('Program stopped. Press {YELLOW}Enter{RESET} to exit.')
    clear()
    sys.exit(0)
