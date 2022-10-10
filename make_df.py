import numpy as np
import pandas as pd
import random
import string
from datetime import datetime as dt


def make_df_from_config(df_config):
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