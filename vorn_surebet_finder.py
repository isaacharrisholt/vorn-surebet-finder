# ------------------------------------
# PLANNED SITES:
# Coral
# Paddy Power
# Betfred
# William Hill
# Sky Bet
# bet365
# 888 Sport
# betway
# betVictor
# Unibet
# Smarkets
# ------------------------------------
import time

from multiprocessing import Process, Queue

from lib import two_way, three_way, utils, calculations, ui
from lib.sites import betfair, bwin, ladbrokes

# Sites
site_list = {
    'Betfair': betfair.get_data,
    'bwin': bwin.get_data,
    'Ladbrokes': ladbrokes.get_data
}


# Main function
def main(sport, markets, three_way_markets, total_stake, rounding_base):
    # Create dictionary of sites with translated markets
    sites = {}

    for site in site_list:
        sites[site] = {
            'fn': site_list[site],
            'args': [
                sport,
                [utils.translate_to_site_market(market, site) for market in markets]
            ]
        }

    # Create queue for multiprocessing
    q = Queue()

    # List of jobs
    jobs = []

    # Create jobs, start them and join the queue
    for site in sites:
        args = [q] + sites[site]['args']
        p = Process(target=sites[site]['fn'], args=args)
        print(f'- {site}: Creating job')
        jobs.append(p)
        p.start()

    # Will store output of queue processes
    df_dicts = []

    # Get results from functions
    for j in jobs:
        df_dicts.append(q.get())

    # Combine dictionary results into single dictionary
    results = {}
    for df_dict in df_dicts:
        results.update(df_dict)

    # Translate columns back
    for broker in results:
        results[broker] = utils.translate_columns(results[broker], broker)
        # print(f'\n\n\n{broker}')
        # print(results[broker])

    # Dictionary to store all surebets
    all_surebets = {}

    # Boolean to store if we have any surebets
    surebets_found = False

    for market in markets:
        # Check if this is a three way market
        if market in three_way_markets:
            market_surebets, success = three_way.get_surebets(results, market)
        else:
            market_surebets, success = two_way.get_surebets(results, market)

        # If a surebet was found, update boolean
        if success:
            surebets_found = True

            # Store the surebets
            all_surebets[market] = market_surebets

    # Apply calculations to surebets found, if any, then present to user
    if surebets_found:
        all_surebets = calculations.do_surebet_calculations(all_surebets, three_way_markets, total_stake, rounding_base)
        ui.present_surebets(all_surebets, sport)


if __name__ == '__main__':
    # Clear console of commands
    utils.clear()

    try:
        # Initiate the program by getting values
        sport, markets, three_way_markets = ui.get_sport()
        total_stake = ui.get_total_stake()
        rounding_base = ui.get_rounding_base()

        # Get wait time between surebet checks
        wait_time = ui.get_wait_time()
    except (RuntimeError, KeyboardInterrupt, EOFError):
        utils.quit_program()

    # Run on a loop until user stops the program
    while True:
        # Separate timer variable
        timer = wait_time

        try:
            # Run surebet program
            utils.clear()
            main(sport, markets, three_way_markets, total_stake, rounding_base)
        except (KeyboardInterrupt, InterruptedError):
            utils.quit_program()

        try:
            # Wait until next cycle
            while timer > 0:
                utils.clear()
                utils.pprint(f'Waiting for {timer} more seconds...\n'
                             f'Press Ctrl+C or Cmd+C to check surebets again now.')
                timer -= 1
                time.sleep(1)
        except KeyboardInterrupt:
            pass
