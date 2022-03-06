import pandas as pd
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from datetime import date


def load_data():
    # Paths
    shooting_path = '../backend/data/inputs/3p/shooting.csv'
    game_totals_path = '../backend/data/inputs/3p/game_totals.csv'
    game_details_path = '../backend/data/inputs/3p/game_details.csv'

    # Read files
    shooting_df = pd.read_csv(shooting_path)
    game_totals_df = pd.read_csv(game_totals_path)
    game_details_df = pd.read_csv(game_details_path)

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

    return df


def random_forest_model():
    # Load data
    data = load_data()

    # Extract current games
    data['date'] = data['date'].apply(
        lambda x: date(int(x.split('-')[0]), int(x.split('-')[1]), int(x.split('-')[2]))
    )
    current_date = date.today()
    today_games = data[data['date'] == current_date].drop(['date', 'visitor', 'home', 'target'], axis=1)
    data = data[data['date'] != current_date].drop(['date', 'visitor', 'home'], axis=1)

    # Target and features
    y = data.iloc[:, 0]
    X = data.iloc[:, 1:]

    # Split data into testing and training sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = RandomForestRegressor(
        random_state=0,
        n_estimators=20, max_depth=3,
        max_features=15, max_samples=2000,
        min_samples_split=500
    )

    model.fit(X_train, y_train)

    # Evaluate model
    evaluate_model(X_test, y_test, model)

    return model.predict(today_games)


def evaluate_model(X_test, y_test, model):
    # Predict
    predictions = model.predict(X_test)

    # Evaluate
    r2 = round(r2_score(y_test, predictions), 2)
    mse = round(mean_squared_error(y_test, predictions), 2)
    rmse = round(mean_squared_error(y_test, predictions, squared=False), 2)
    mae = round(mean_absolute_error(y_test, predictions), 2)
    evaluations_df = pd.DataFrame({'metric': ['r2', 'mse', 'rmse', 'mae'],
                                   'score': [r2, mse, rmse, mae]})

    print('\nRandom Forest')
    print(evaluations_df)


if __name__ == '__main__':
    random_forest = random_forest_model()
    print(random_forest)
