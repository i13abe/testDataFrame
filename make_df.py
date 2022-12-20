import numpy as np
import pandas as pd
import random
import string
from datetime import datetime as dt


def make_df_from_config(df_config):
    """
    Generating DataFrame with random values from config (Dict).
    Args:
        df_config (Dict) : config data
    Returms:
        df  (pd.DataFrame)
    """
    num_rows = df_config['num_rows']
    df = pd.DataFrame()
    df_features = df_config['features']
    
    for feature_name in df_features.keys():
        features = []
        nan_rate = df_features[feature_name]['NaN rate']
        dtype = df_features[feature_name]['Dtype']
        if dtype=='str':
            unique = df_features[feature_name]['Unique']
            if unique=="Random letter":
                for i in range(num_rows):
                    random_list = [random.choice(string.ascii_lowercase) for n in range(df_features[feature_name]['Char digits'])]
                    features.append("".join(random_list))
            elif unique=="Random number":
                for i in range(num_rows):
                    random_int = random.randint(df_features[feature_name]['Min'], df_features[feature_name]['Max'])
                    features.append(str(random_int).zfill(df_features[feature_name]['Char digits']))
            elif unique=="Seaquential number":
                start = df_features[feature_name]['Start']
                features = [
                    str(i).zfill(df_features[feature_name]['Char digits'])
                    for i in range(start, start+num_rows)
                ]
            elif unique=="yourself":
                features = random.choices(df_features[feature_name]['Unique list'].split(','), k=num_rows)
            features = np.array(features)
        elif dtype=='int':
            for i in range(num_rows):
                random_int = random.randint(df_features[feature_name]['Min'], df_features[feature_name]['Max'])
                features.append(random_int)
            features = np.array(features)
            if nan_rate!=0:
                print(f'On the int column "{feature}", np.nan are detected. This column is converted to float.')
                features = features.astype(float)
        elif dtype=='float':
            for i in range(num_rows):
                random_int = random.uniform(df_features[feature_name]['Min'], df_features[feature_name]['Max'])
                features.append(random_int)
            features = np.array(features)
        elif dtype=='datetime':
            freq = df_features[feature_name]['Freq'][0]
            date = pd.date_range(start=df_features[feature_name]['Start'], end=df_features[feature_name]['End'], freq=freq)
            date = np.tile(date.values, num_rows//len(date)+1)
            features = date[:num_rows]
        
        df[feature_name] = features

        if nan_rate!=0:
            nan_idx = random.sample(range(num_rows), round(num_rows*nan_rate))
            features[feature_name][nan_idx] = np.nan
    return df


def make_config_from_df(
    df,
):
    """
    Generate config from DataFrame.
    Args:
        df (pd.DataFrame)
    Returns:
        df_config (Dict) : config data
    """

    df_config = {}
    df_config['df_name'] = 'test_df'
    df_config['num_rows'] = len(df)
    df_config['features'] = {}

    for col in df.columns:
        df_config['features'][col] = {}
        df_config['features'][col]['Nan rate'] = df[col].isnull().sum()/len(df)
        if 'int' in str(df[col].dtype):
            df_config['features'][col]['Dtype'] = 'int'
            df_config['features'][col]['Max'] = df[col].max()
            df_config['features'][col]['Min'] = df[col].min()
        elif 'float' in str(df[col].dtype):
            if all(df[col].dropna().applymap(lambda x: x.is_integer())):
                df_config['features'][col]['Dtype'] = 'int'
            else:
                df_config['features'][col]['Dtype'] = 'float'
            df_config['features'][col]['Max'] = df[col].max()
            df_config['features'][col]['Min'] = df[col].min()
        else:
            df_config['features'][col]['Dtype'] = 'str'
            df[col].astype(str)
            if all(df[col].str.isdigit()):
                df_config['features'][col]['Unique'] = 'Random number'
                df_config['features'][col]['Max'] = df[col].astype(float).max()
                df_config['features'][col]['Min'] = df[col].astype(float).min()
                df_config['features'][col]['Char digits'] = df[col].astype(str).apply(len).max()
            elif df[col].nunique() <= 30:
                df_config['features'][col]['Unique'] = 'yourself'
                df_config['features'][col]['Unique list'] = ','.join(df[col].unique())
            else:
                df_config['features'][col]['Unique'] = 'Random letter'
                df_config['features'][col]['Char digits'] = df[col].astype(str).apply(len).max()
    return df_config