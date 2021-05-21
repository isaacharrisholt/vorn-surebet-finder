from sympy import symbols, solve, Eq

from . import utils


# Unrounded calculations for two way bets
def two_way_unrounded_calculations(odds1, odds2, total_stake):
    x, y = symbols('x y')

    # Equation for total stake
    total_stake_eq = Eq(x + y - total_stake, 0)

    # Odds multiplied by their stake must be equal
    individual_stakes_eq = Eq((odds2 * y) - (odds1 * x), 0)

    # Solve equations to get stakes and return
    stakes = solve((total_stake_eq, individual_stakes_eq), (x, y))
    stake1 = float(stakes[x])
    stake2 = float(stakes[y])
    return stake1, stake2


# Recalculate two way bet values with rounding
def two_way_rounded_calculations(odds1, odds2, stake1, stake2, total_stake, rounding_base):
    # New values for stakes
    stake1 = utils.round_to(stake1, rounding_base)
    stake2 = utils.round_to(stake2, rounding_base)

    # Stakes should add to less than total stake, if not, recalculate
    if stake1 + stake2 > total_stake:
        stake2 = total_stake - stake1

    # Calculate profits and percentage benefits
    profit1 = odds1 * stake1 - total_stake
    profit2 = odds2 * stake2 - total_stake
    benefit1 = f'{profit1 / total_stake * 100:.2f}%'
    benefit2 = f'{profit2 / total_stake * 100:.2f}%'

    # Create and return a dictionary storing the values
    values_dict = {
        'Odds 1': odds1,
        'Odds 2': odds2,
        'Stake 1': stake1,
        'Stake 2': stake2,
        'Profit 1': profit1,
        'Profit 2': profit2,
        'Benefit 1': benefit1,
        'Benefit 2': benefit2
    }
    return values_dict


# Unrounded calculations for three way bets
def three_way_unrounded_calculations(odds1, odds2, odds3, total_stake):
    x, y, z = symbols('x y z')

    # Equation for total stake
    total_stake_eq = Eq(x + y + z - total_stake, 0)

    # Odds multiplied by their stake must be equal
    individual_stakes_eq1 = Eq((odds2 * y) - (odds1 * x), 0)
    individual_stakes_eq2 = Eq((odds3 * z) - (odds2 * y), 0)

    # Solve equations to get stakes and return
    stakes = solve((total_stake_eq, individual_stakes_eq1, individual_stakes_eq2), (x, y, z))
    stake1 = float(stakes[x])
    stake2 = float(stakes[y])
    stake3 = float(stakes[z])
    return stake1, stake2, stake3


# Recalculate three way bet values with rounding
def three_way_rounded_calculations(odds1, odds2, odds3, stake1, stake2, stake3, total_stake, rounding_base):
    # New values for stakes
    stake1 = utils.round_to(stake1, rounding_base)
    stake2 = utils.round_to(stake2, rounding_base)
    stake3 = utils.round_to(stake3, rounding_base)

    # Stakes should add to less than total stake, if not, recalculate
    if stake1 + stake2 + stake3 > total_stake:
        stake3 = total_stake - (stake1 + stake2)

    # Calculate profits and percentage benefits
    profit1 = odds1 * stake1 - total_stake
    profit2 = odds2 * stake2 - total_stake
    profit3 = odds3 * stake3 - total_stake
    benefit1 = f'{profit1 / total_stake * 100:.2f}%'
    benefit2 = f'{profit2 / total_stake * 100:.2f}%'
    benefit3 = f'{profit3 / total_stake * 100:.2f}%'

    # Create and return a dictionary storing the values
    values_dict = {
        'Odds 1': odds1,
        'Odds 2': odds2,
        'Odds 3': odds3,
        'Stake 1': stake1,
        'Stake 2': stake2,
        'Stake 3': stake3,
        'Profit 1': profit1,
        'Profit 2': profit2,
        'Profit 3': profit3,
        'Benefit 1': benefit1,
        'Benefit 2': benefit2,
        'Benefit 3': benefit3
    }
    return values_dict


# Perform calculations for two way bets
def two_way_bets(surebets_df, bet_dicts, broker_pair, market, total_stake, rounding_base):
    # Need to go through both columns of odds
    for col in [1, 2]:
        for i, value in enumerate(surebets_df[f'{market}_surebets_{col}']):

            # Check that the surebet is in this column
            if not value < 1:
                continue

            # Get odds values
            odds1 = float([utils.convert_odds(odd) for odd in surebets_df.at[i, f'{market}_x'].split('\n')][0])
            odds2 = float([utils.convert_odds(odd) for odd in surebets_df.at[i, f'{market}_y'].split('\n')][1])
            competitors = surebets_df.iloc[i, surebets_df.columns.get_loc('Competitors_x')]

            # Calculate the stakes required and the profit and benefit from the bet
            stake1, stake2 = two_way_unrounded_calculations(odds1, odds2, total_stake)

            # Calculate the same values for the stakes when rounded to the nearest rounding_base
            bet_dict = two_way_rounded_calculations(odds1, odds2, stake1, stake2, total_stake, rounding_base)

            # If rounded values don't result in a profit, bet is unsafe
            if not (bet_dict['Profit 1'] > 0 and bet_dict['Profit 2'] > 0):
                print('Found unsafe bet, discarding')
                continue

            # Save to bet_dicts with competitors as key
            bet_dicts[market][broker_pair][competitors] = bet_dict

    return bet_dicts


# Perform calculations for three way bets
def three_way_bets(surebets_df, bet_dicts, broker_pair, market, total_stake, rounding_base):
    # Need to go through both columns of odds
    for col in [1, 2, 3, 4, 5, 6]:
        for i, value in enumerate(surebets_df[f'{market}_surebets_{col}']):

            # Check that the surebet is in this column
            if not value < 1:
                continue

            # Get odds values
            odds1 = float([utils.convert_odds(odd) for odd in surebets_df.at[i, f'{market}_x'].split('\n')][0])
            odds2 = float([utils.convert_odds(odd) for odd in surebets_df.at[i, f'{market}_y'].split('\n')][1])
            odds3 = float([utils.convert_odds(odd) for odd in surebets_df.at[i, f'{market}_y'].split('\n')][2])
            competitors = surebets_df.iloc[i, surebets_df.columns.get_loc('Competitors_x')]

            # Calculate the stakes required and the profit and benefit from the bet
            stake1, stake2, stake3 = three_way_unrounded_calculations(odds1, odds2, odds3, total_stake)

            # Calculate the same values for the stakes when rounded to the nearest rounding_base
            bet_dict = three_way_rounded_calculations(odds1, odds2, odds3, stake1, stake2, stake3, total_stake,
                                                      rounding_base)

            # If rounded values don't result in a profit, bet is unsafe
            if not (bet_dict['Profit 1'] > 0 and bet_dict['Profit 2'] > 0 and bet_dict['Profit 3'] > 0):
                print('Found unsafe bet, discarding')
                continue

            # Save to bet_dicts with competitors as key
            bet_dicts[market][broker_pair][competitors] = bet_dict

    return bet_dicts


# Function to calculate stakes, profit etc. for each surebet
def do_surebet_calculations(all_surebets, three_way_markets, total_stake, rounding_base):
    # Create dictionary to store bet dataframes
    bet_dicts = {}

    # Iterate through markets in dictionary
    for market in all_surebets:
        bet_dicts[market] = {}

        # Iterate through broker pairs in market
        for broker_pair in all_surebets[market]:
            surebets_df = all_surebets[market][broker_pair]
            bet_dicts[market][broker_pair] = {}

            if market in three_way_markets:
                bet_dicts = three_way_bets(surebets_df, bet_dicts, broker_pair, market, total_stake, rounding_base)
            else:
                bet_dicts = two_way_bets(surebets_df, bet_dicts, broker_pair, market, total_stake, rounding_base)

    # Finally, return the dictionary of surebets with profits
    return bet_dicts
