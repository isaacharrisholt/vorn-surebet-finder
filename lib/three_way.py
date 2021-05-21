import pandas as pd
from fuzzywuzzy import process, fuzz

from . import utils


# Clean up the dataframes and just get the markets we want
def format_df(df, market):
    new_df = df[['Competitors', market]]

    # Replace empty odds and odds with just one value
    new_df = new_df.replace(r'', '1\n1\n1', regex=True)
    new_df = new_df.replace(r'^\d+\.d+$', '1\n1\n1', regex=True)
    new_df.dropna(inplace=True)
    return new_df


# Match competitor names between all three dataframes
def match_competitors(df1, df2, df3):
    # Create lists of competitor names for string matching
    competitors2 = df2['Competitors'].tolist()
    competitors3 = df3['Competitors'].tolist()

    # Match strings with df2
    df1[['Matched Competitors 1', 'Matching Score 1']] = df1['Competitors'].apply(
        lambda x: process.extractOne(x, competitors2, scorer=fuzz.token_set_ratio)).apply(pd.Series)

    # Match strings with df3
    df1[['Matched Competitors 2', 'Matching Score 2']] = df1['Matched Competitors 1'].apply(
        lambda x: process.extractOne(x, competitors3, scorer=fuzz.token_set_ratio)).apply(pd.Series)

    return df1


# Create surebet dataframe
def get_surebet_df(df1, df2, df3, market):
    # Merge df1 and df2
    df1_and_2 = pd.merge(df1, df2, left_on='Matched Competitors 1', right_on='Competitors')

    # Merge with df3
    surebet_df = pd.merge(df1_and_2, df3, left_on='Matched Competitors 2', right_on='Competitors')

    # Rename the columns to make them easier to deal with later
    rename = {'Competitors': 'Competitors_z', market: f'{market}_z'}
    surebet_df = surebet_df.rename(columns=rename)

    # Filter out where matching scores are low
    surebet_df = surebet_df[(surebet_df['Matching Score 1'] > 60) & (surebet_df['Matching Score 2'] > 60)]

    # Only keep columns we need
    surebet_df = surebet_df[['Competitors_x', f'{market}_x',
                             'Competitors_y', f'{market}_y',
                             'Competitors_z', f'{market}_z']]

    return surebet_df


# Formula to find surebets in dataframes
def find_surebets(surebet_df, market):
    letters = ['x', 'y', 'z']
    numbers = ['1', '2', '3']

    # Separate odds out into three columns
    for letter in letters:
        surebet_df[[f'{market}_{letter}_1',
                    f'{market}_{letter}_2',
                    f'{market}_{letter}_3']] = surebet_df[f'{market}_{letter}'].apply(utils.replace_comma) \
                                                           .str.split('\n', expand=True).iloc[:, 0:3].apply(pd.Series)
        for i in [1, 2, 3]:
            surebet_df[f'{market}_{letter}_{i}'] = surebet_df[f'{market}_{letter}_{i}'].apply(utils.convert_odds) \
                                                                                       .astype(float)

    # Add reciprocals of odds combinations
    count = 0

    for p in numbers:
        for q in numbers:

            # Check we're not using the same odds
            if p == q:
                continue

            for r in numbers:

                # Check again...
                if q == r or p == r:
                    continue

                # Add to the count
                count += 1

                # Add the reciprocals of odds combinations
                surebet_df[f'{market}_surebets_{count}'] = (1 / surebet_df[f'{market}_x_{p}']) + \
                                                           (1 / surebet_df[f'{market}_y_{q}']) + \
                                                           (1 / surebet_df[f'{market}_z_{r}'])

    # Clean up the frame
    surebet_columns = [f'{market}_surebets_{i + 1}' for i in range(count)]
    surebet_columns = ['Competitors_x', f'{market}_x', 'Competitors_y', f'{market}_y', 'Competitors_z', f'{market}_z']\
                      + surebet_columns
    surebet_df = surebet_df[surebet_columns]

    # Remove anything that isn't a surebet
    surebet_df = surebet_df[(surebet_df[f'{market}_surebets_1'] < 1) | (surebet_df[f'{market}_surebets_2'] < 1) |
                            (surebet_df[f'{market}_surebets_3'] < 1) | (surebet_df[f'{market}_surebets_4'] < 1) |
                            (surebet_df[f'{market}_surebets_5'] < 1) | (surebet_df[f'{market}_surebets_6'] < 1)]

    # Reset index and return
    surebet_df.reset_index(drop=True, inplace=True)
    return surebet_df


# Function to get surebets in a set of dataframes
def get_surebets(odds_dfs, market):
    # Boolean to return if surebets were found
    success = True

    # Set some pandas options
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    # Create new dictionary with copies of results
    copied_dfs = {}

    # Format our dataframes
    for broker in odds_dfs:
        copied_dfs[broker] = odds_dfs[broker].copy()
        copied_dfs[broker] = format_df(copied_dfs[broker], market)

    # Store dataframe pairs that have been checked already
    checked_combos = []

    # Dictionary to store surebets
    surebets_dict = {}

    # Start iterating through dataframes
    for broker1 in copied_dfs:
        df1 = copied_dfs[broker1].copy()

        for broker2 in copied_dfs:
            df2 = copied_dfs[broker2].copy()

            # Check if this is the same as first broker, if so continue
            if broker2 == broker1:
                continue

            for broker3 in copied_dfs:
                df3 = copied_dfs[broker3].copy()

                # If both brokers are the same, skip
                if broker3 == broker2 or broker3 == broker1:
                    continue

                sorted_brokers = sorted([broker1, broker2, broker3])

                # If we've already checked this dataframe combo, skip
                if sorted_brokers in checked_combos:
                    continue

                # Make sure we don't check this combo again
                checked_combos.append(sorted_brokers)

                # Store name of dataframe combo for reference
                combo_name = '-'.join(sorted([broker1, broker2, broker3]))

                # Match strings in out dataframes
                df1 = match_competitors(df1, df2, df3)

                # Create a combined surebet dataframe
                surebet_df = get_surebet_df(df1, df2, df3, market)

                # Find surebets
                surebet_df = find_surebets(surebet_df, market)

                # Drop rows with NaN due to missing data
                surebet_df.dropna(inplace=True)

                # Save result
                if not surebet_df.empty:
                    surebets_dict[combo_name] = surebet_df

    if not surebets_dict:
        print(f'No surebets found for {market.title()}!')
        success = False

    return surebets_dict, success
