import json
import beepy

from . import utils


# Gets chosen sport from user and return along with available markets
def get_sport():
    # Gets list of sports
    with open('files/sports_and_markets.json') as sports_and_markets_file:
        sports_and_markets = json.load(sports_and_markets_file)

    # Available sports
    available_sports = [sport for sport in sports_and_markets]

    chosen_sport = "Hey, you found me, but I'm not a sport!"

    # Ask user for sport until they give a valid one
    while True:
        chosen_sport = utils.pinput('Which sport would you like to check for surebets?\nPlease choose from the options '
                                    'below:\n' + ', '.join([sport for sport in available_sports])).strip().title()
        utils.clear()

        # Check if input was invalid, else let function continue
        if chosen_sport not in available_sports:
            utils.pprint('{RED}Invalid sport, please try again.{RESET}')
            continue

        # Get markets for sport
        two_way_markets = sports_and_markets[chosen_sport]['two-way']
        three_way_markets = sports_and_markets[chosen_sport]['three-way']

        # Variable containing all markets
        markets = two_way_markets + three_way_markets

        # Boolean for whether match result is a three way bet, and if it is, append to three way markets
        win_is_three_way = sports_and_markets[chosen_sport]['win-bet-is-three-way']
        if win_is_three_way:
            three_way_markets.append('win')

        # Return values
        return chosen_sport, markets, three_way_markets


# Get the total stake
def get_total_stake():
    while True:
        total_stake = utils.pinput('What would you like your total stake to be (sum of all bet amounts per surebet)?\n'
                                   'Note: please just input a whole number without a currency symbol.')
        utils.clear()

        try:
            total_stake = int(total_stake)
            break
        except ValueError:
            utils.pprint('{RED}Invalid input, please try again.{RESET}')

    return total_stake


# Get the rounding base
def get_rounding_base():
    while True:
        total_stake = utils.pinput('In order to make bets seem more real to brokers, each individual stake will be '
                                   'rounded to the nearest X amount.\n'
                                   'Please input, in a whole number, what you would like this X to be.\n'
                                   'We recommend around 5% of your total stake (e.g. 5 if your total stake is 100).')
        utils.clear()

        try:
            total_stake = int(total_stake)
            break
        except ValueError:
            utils.pprint('{RED}Invalid input, please try again.{RESET}')

    return total_stake


# Get wait time between checking for surebets
def get_wait_time():
    while True:
        wait_time = utils.pinput('How often, in whole minutes, would you like to check for surebets?')
        utils.clear()

        try:
            wait_time = int(wait_time)
            break
        except ValueError:
            utils.pprint('{RED}Invalid input, please try again.{RESET}')

    return wait_time * 60


# Presents surebets nicely to user
def present_surebets(all_surebets):
    utils.clear()

    # List to store generated strings for all markets
    surebet_market_strings = []

    for market in all_surebets:
        market_formatted = utils.translate_to_site_market(market, 'Betfair')  # Using Betfair just because

        # List to store surebets for all pairs
        surebet_pair_strings = []

        for pair in all_surebets[market]:

            # List to store surebets for competitor names
            surebet_names_strings = []

            for names in all_surebets[market][pair]:
                # Check that values aren't empty
                if not all_surebets[market][pair][names]:
                    continue

                # Get values from pair and put in list
                values = []

                for key in all_surebets[market][pair][names]:
                    value = f'{key}: {all_surebets[market][pair][names][key]}'
                    values.append(value)

                # Create names string
                names_string = f'        {names}:\n' \
                               f'            ' + '\n            '.join(values)
                surebet_names_strings.append(names_string)

            # Check for emptiness
            if not surebet_names_strings:
                continue

            # Create pair string
            pair_string = f'    {pair}:\n' + '\n'.join(surebet_names_strings)
            surebet_pair_strings.append(pair_string)

        # Check for emptiness
        if not surebet_pair_strings:
            continue

        # Create market string
        market_string = f'{market_formatted}:\n' + '\n'.join(surebet_pair_strings)
        surebet_market_strings.append(market_string)

    # If everything is empty, just return out
    if not surebet_market_strings:
        return

    # Join all strings
    final_string = 'SUREBETS FOUND!\n\n' + '\n\n'.join(surebet_market_strings) + \
                   '\n\nPress {YELLOW}Enter{RESET} to continue.'

    # Present to user
    utils.pprint(final_string)
    beepy.beep(sound='success')
    input(': ')
