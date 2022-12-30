import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error


def load_data():
    # Paths
    shooting_path = 'backend/data/inputs/3p/shooting.csv'
    game_totals_path = 'backend/data/inputs/3p/game_totals.csv'
    game_details_path = 'backend/data/inputs/3p/game_details.csv'

    # Read files
    shooting_df = pd.read_csv(shooting_path).drop(['Unnamed: 0'], axis=1)
    game_totals_df = pd.read_csv(game_totals_path).drop(['Unnamed: 0'], axis=1)
    game_details_df = pd.read_csv(game_details_path).drop(['Unnamed: 0'], axis=1)

    # Merge files
    cols_to_use = list(game_totals_df.columns.difference(shooting_df.columns)) + ['date', 'visitor', 'home']
    df = pd.merge(shooting_df, game_totals_df[cols_to_use],
                  left_on=['date', 'visitor', 'home'],
                  right_on=['date', 'visitor', 'home'],
                  how='left')

    cols_to_use = list(game_details_df.columns.difference(df.columns)) + ['date', 'visitor', 'home']
    df = pd.merge(df, game_details_df[cols_to_use],
                  left_on=['date', 'visitor', 'home'],
                  right_on=['date', 'visitor', 'home'],
                  how='left')

    df['date'] = pd.to_datetime(df['date'])

    return df.fillna(0)


def neural_network_model():
    # Load data
    data = load_data()

    # Extract current games
    next_game = data['date'].max()
    next_slate = data[data['date'] == next_game].drop(['date', 'visitor', 'home', 'target'], axis=1)
    data = data[data['date'] != next_game].drop(['date', 'visitor', 'home'], axis=1)

    # Target and features
    y = data.iloc[:, 0]
    X = data.iloc[:, 1:]

    # Standardize X
    scale = StandardScaler()
    scale.fit(X)
    X = scale.transform(X)
    next_slate = scale.transform(next_slate)

    # Split data into testing and training sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    nn_model = MLPRegressor(
        batch_size=300, max_iter=200,
        learning_rate='adaptive', learning_rate_init=.01,
        hidden_layer_sizes=(100,), solver='adam',
        random_state=0,
    )

    nn_model.fit(X_train, y_train)

    # Evaluate model
    evaluate_model(X_test, y_test, nn_model)

    return nn_model.predict(next_slate)


def evaluate_model(X_test, y_test, nn_model):
    # Predict
    predictions = nn_model.predict(X_test)

    # Evaluate
    r2 = round(r2_score(y_test, predictions), 2)
    mse = round(mean_squared_error(y_test, predictions), 2)
    rmse = round(mean_squared_error(y_test, predictions, squared=False), 2)
    mae = round(mean_absolute_error(y_test, predictions), 2)
    evaluations_df = pd.DataFrame({'metric': ['r2', 'mse', 'rmse', 'mae'],
                                   'score': [r2, mse, rmse, mae]})

    print('\nNeural Network')
    print(evaluations_df)


if __name__ == '__main__':
    model = neural_network_model()
    print(model)