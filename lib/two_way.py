import pandas as pd
from fuzzywuzzy import process, fuzz
from sympy import symbols, solve, Eq

from . import utils


# Clean up the dataframes and just get the markets we want
def format_df(df, market):
    new_df = df[['Competitors', market]]

    # Replace empty odds and odds with just one value and remove goal numbers
    new_df = new_df.replace(r'', '1\n1', regex=True)
    new_df = new_df.replace(r'^\d+\.d+$', '1\n1', regex=True)
    new_df[market] = new_df[market].apply(lambda x: '\n'.join(x.split('\n')[-2:]) if len(x.split('\n')) > 2 else x)
    new_df.dropna(inplace=True)
    return new_df


# Match competitor names between both dataframes with fuzzywuzzy
def match_competitors(df1, df2):
    # Create list of competitor names for string matching
    competitors2 = df2['Competitors'].tolist()

    # Match strings with fuzzywuzzy
    df1[['Matched Competitors', 'Matching Score']] = df1['Competitors'].apply(
        lambda x: process.extractOne(x, competitors2, scorer=fuzz.token_set_ratio)).apply(pd.Series)
    return df1


# Create surebet dataframe
def get_surebet_df(df1, df2, market):
    # Merge, eliminate non-matching competitors and select only the columns we need
    surebet_df = pd.merge(df1, df2, left_on='Matched Competitors', right_on='Competitors')
    surebet_df = surebet_df[surebet_df['Matching Score'] > 60]
    surebet_df = surebet_df[['Competitors_x', f'{market}_x', 'Competitors_y', f'{market}_y']]
    return surebet_df


# Formula to find surebets in dataframes
def find_surebets(surebet_df, market):
    # Separate odds into separate columns and clean
    # x column
    surebet_df[[f'{market}_x_1',
                f'{market}_x_2']] = surebet_df[f'{market}_x'].apply(utils.replace_comma).str.split('\n', expand=True) \
                                                             .iloc[:, 0:2].apply(pd.Series)
    surebet_df[f'{market}_x_1'] = surebet_df[f'{market}_x_1'].apply(utils.convert_odds).astype(float)
    surebet_df[f'{market}_x_2'] = surebet_df[f'{market}_x_2'].apply(utils.convert_odds).astype(float)
    # y column
    surebet_df[[f'{market}_y_1',
                f'{market}_y_2']] = surebet_df[f'{market}_y'].apply(utils.replace_comma).str.split('\n', expand=True) \
                                                             .iloc[:, 0:2].apply(pd.Series)
    surebet_df[f'{market}_y_1'] = surebet_df[f'{market}_y_1'].apply(utils.convert_odds).astype(float)
    surebet_df[f'{market}_y_2'] = surebet_df[f'{market}_y_2'].apply(utils.convert_odds).astype(float)

    # Add reciprocals of odds pairs
    surebet_df[f'{market}_surebets_1'] = (1 / surebet_df[f'{market}_x_1']) + (1 / surebet_df[f'{market}_y_2'])
    surebet_df[f'{market}_surebets_2'] = (1 / surebet_df[f'{market}_x_2']) + (1 / surebet_df[f'{market}_y_1'])

    # Clean frame
    surebet_df = surebet_df[['Competitors_x', f'{market}_x', 'Competitors_y', f'{market}_y', f'{market}_surebets_1',
                             f'{market}_surebets_2']]

    # Remove non-surebets and reset index
    surebet_df = surebet_df[(surebet_df[f'{market}_surebets_1'] < 1) | (surebet_df[f'{market}_surebets_2'] < 1)]
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
    checked_pairs = []

    # Dictionary to store surebets
    surebets_dict = {}

    # Start iterating through our dataframes
    for broker1 in copied_dfs:
        df1 = copied_dfs[broker1].copy()

        for broker2 in copied_dfs:
            df2 = copied_dfs[broker2].copy()

            # Store name of dataframe pair for reference
            pair_name = '-'.join(sorted([broker1, broker2]))

            # If we've already checked this dataframe pair, or both are the same dataframe, skip
            if pair_name in checked_pairs or broker2 == broker1:
                continue

            # Make sure we don't check this pair again
            checked_pairs.append(pair_name)

            # Match strings in our dataframes
            df1 = match_competitors(df1, df2)

            # Create a combined surebet dataframe
            surebet_df = get_surebet_df(df1, df2, market)

            # Find surebets
            surebet_df = find_surebets(surebet_df, market)

            # Drop rows with NaN due to missing data
            surebet_df.dropna(inplace=True)

            # Save result
            if not surebet_df.empty:
                surebets_dict[pair_name] = surebet_df

    if not surebets_dict:
        print(f'No surebets found for {market.title()}!')
        success = False

    return surebets_dict, success
