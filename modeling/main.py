import pandas as pd
from datetime import date

from linear_regression import linear_model
from decision_tree_regression import decision_tree_model
from gradient_boosted_regression import gradient_boosted_model
from nn import neural_network_model
from random_forest_regression import random_forest_model
from linear_regression import load_data


def main():
    # Compute predictions
    linear = linear_model()
    decision_tree = decision_tree_model()
    gradient_boosted = gradient_boosted_model()
    neural_network = neural_network_model()
    random_forest = random_forest_model()

    # Extract current games
    data = load_data()
    data['date'] = data['date'].apply(
        lambda x: date(int(x.split('-')[0]), int(x.split('-')[1]), int(x.split('-')[2]))
    )
    current_date = date.today()
    today_games = data[data['date'] == current_date]

    df = today_games[['date', 'visitor', 'home']].copy()
    df.loc[:, 'linear'] = [round(x) for x in linear]
    df.loc[:, 'decision_tree'] = [round(x) for x in decision_tree]
    df.loc[:, 'gradient_boosted'] = [round(x) for x in gradient_boosted]
    df.loc[:, 'neural_network'] = [round(x) for x in neural_network]
    df.loc[:, 'random_forest'] = [round(x) for x in random_forest]

    predictions = pd.read_csv('../backend/predictions/3p_predictions.csv').drop(['Unnamed: 0'], axis=1)
    predictions['date'] = predictions['date'].apply(
        lambda x: date(int(x.split('/')[2]), int(x.split('/')[0]), int(x.split('/')[1]))
    )
    predictions = predictions.append(df, ignore_index=True)
    predictions = predictions.drop_duplicates(['date', 'visitor', 'home'], keep='last')
    predictions['avg'] = \
        (predictions['linear'] + predictions['decision_tree'] + predictions['gradient_boosted'] +
         predictions['neural_network'] + predictions['random_forest']) / 5

    predictions.to_csv('../backend/predictions/3p_predictions.csv')


if __name__ == '__main__':
    main()
