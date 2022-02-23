import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error


def load_data():
    # Paths
    shooting_path = 'backend/data/inputs/shooting.csv'
    game_totals_path = 'backend/data/inputs/game_totals.csv'
    advanced_totals_path = 'backend/data/inputs/advanced_totals.csv'
    game_details_path = 'backend/data/inputs/game_details.csv'
    advanced_details_path = 'backend/data/inputs/advanced_details.csv'

    # Read files
    shooting_df = pd.read_csv(shooting_path)
    game_totals_df = pd.read_csv(game_totals_path)
    advanced_totals_df = pd.read_csv(advanced_totals_path)
    game_details_df = pd.read_csv(game_details_path)
    advanced_details_df = pd.read_csv(advanced_details_path)

    # Merge files
    cols_to_use = list(game_totals_df.columns.difference(shooting_df.columns)) + ['date', 'visitor', 'home']
    df = pd.merge(shooting_df, game_totals_df[cols_to_use],
                  left_on=['date', 'visitor', 'home'],
                  right_on=['date', 'visitor', 'home'],
                  how='left')

    cols_to_use = list(advanced_totals_df.columns.difference(df.columns)) + ['date', 'visitor', 'home']
    df = pd.merge(df, advanced_totals_df[cols_to_use],
                  left_on=['date', 'visitor', 'home'],
                  right_on=['date', 'visitor', 'home'],
                  how='left')

    cols_to_use = list(game_details_df.columns.difference(df.columns)) + ['date', 'visitor', 'home']
    df = pd.merge(df, game_details_df[cols_to_use],
                  left_on=['date', 'visitor', 'home'],
                  right_on=['date', 'visitor', 'home'],
                  how='left')

    cols_to_use = list(advanced_details_df.columns.difference(df.columns)) + ['date', 'visitor', 'home']
    df = pd.merge(df, advanced_details_df[cols_to_use],
                  left_on=['date', 'visitor', 'home'],
                  right_on=['date', 'visitor', 'home'],
                  how='left')

    return df.drop(['date', 'visitor', 'home'], axis=1)


def linear_model():
    # Load data
    data = load_data()

    # Target and features
    y = data.iloc[:, 0]
    X = data.iloc[:, 1:]

    # Standardize X
    X = StandardScaler().fit_transform(X)

    # Split data into testing and training sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Evaluate model
    evaluate_model(X_test, y_test, model)

    return model


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

    print(evaluations_df)


if __name__ == '__main__':
    model = linear_model()



