import pandas as pd
import numpy as np
from itertools import product
from scipy.stats import pearsonr


def preprocess():
    # Load data
    df = pd.read_csv('backend/data/details/advanced_details.csv').drop(['Unnamed: 0'], axis=1)
    shooting_df = pd.read_csv('backend/data/totals/game_totals.csv').drop(['Unnamed: 0'], axis=1)
    shooting_df = shooting_df[['date', 'visitor', 'home', 'team', '3p']]




if __name__ == '__main__':
    preprocess()
