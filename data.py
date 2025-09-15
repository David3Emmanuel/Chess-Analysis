import pandas as pd
import numpy as np

def load_data():
    df = pd.read_csv('tournament_results.csv')

    numerical_columns = df.select_dtypes(include=[np.number, bool]).columns.tolist()
    df_numerical = df[numerical_columns].copy()
    eval_column = df_numerical['eval'].copy()
    df_numerical = df_numerical.drop('eval', axis=1)

    print("Processed data shape:", df_numerical.shape)
    print("Processed columns (without eval):", df_numerical.columns.tolist())

    X = df_numerical.values
    y = eval_column.values

    return X, y