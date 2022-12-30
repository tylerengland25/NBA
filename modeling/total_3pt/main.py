import pandas as pd
import numpy as np

from linear_regression import linear_model
from decision_tree_regression import decision_tree_model
from gradient_boosted_regression import gradient_boosted_model
from nn import neural_network_model
from random_forest_regression import random_forest_model
from linear_regression import load_data


def risk(diff):
    # return 1
    if abs(diff) <= .5:
        return 1
    elif abs(diff) <= 1.5:
        return 1.5
    elif abs(diff) <= 2.5:
        return 2
    elif abs(diff) <= 3.5:
        return 2.5
    elif abs(diff) >= 4.5:
        return 3


def main():
    # Compute predictions
    linear = linear_model()
    decision_tree = decision_tree_model()
    gradient_boosted = gradient_boosted_model()
    neural_network = neural_network_model()
    random_forest = random_forest_model()

    # Extract current games
    data = load_data()
    # Extract current games
    next_game = data['date'].max()
    next_slate = data[data['date'] == next_game]

    df = next_slate[['date', 'visitor', 'home']].copy()
    df.loc[:, 'linear'] = [round(x) for x in linear]
    df.loc[:, 'decision_tree'] = [round(x) for x in decision_tree]
    df.loc[:, 'gradient_boosted'] = [round(x) for x in gradient_boosted]
    df.loc[:, 'neural_network'] = [round(x) for x in neural_network]
    df.loc[:, 'random_forest'] = [round(x) for x in random_forest]

    predictions = pd.read_csv('backend/predictions/3p_predictions.csv').drop(['Unnamed: 0'], axis=1).dropna(axis=0, how='all')
    predictions['date'] = pd.to_datetime(predictions['date'])
    predictions = predictions.append(df, ignore_index=True)
    predictions = predictions.drop_duplicates(['date', 'visitor', 'home'], keep='last')
    predictions['avg'] = \
        (predictions['linear'] + predictions['decision_tree'] + predictions['gradient_boosted'] +
         predictions['neural_network'] + predictions['random_forest']) / 5

    models = ['linear', 'decision_tree', 'gradient_boosted', 'neural_network', 'random_forest', 'avg']
    for model in models:
        predictions[f'{model}_diff'] = predictions[f'{model}'] - predictions[f'line']
        predictions[f'{model}_unit'] = predictions[f'{model}_diff'].apply(risk)

    predictions.to_csv('backend/predictions/3p_predictions.csv')


if __name__ == '__main__':
    main()