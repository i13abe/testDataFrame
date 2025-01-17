import numpy as np
import pandas as pd
import random
import string
from datetime import datetime as dt
import json


def upload_file(input_data, **kwargs):
    """
    This is uploader for generating DataFrame.
    input data is expected json path, csv path, pickle path, or DataFrame.
    Args:
        input_data (Union[str, pd.DataFrame]) : json path, csv path, pickle path or DataFrame
        kwargs (Dict) : additional arguments for read csv or read_pickle
    Returns:
        df_dict (Dict) : Config data for generating GUI
    """
    try:
        if isinstance(input_data, str):
            exe = input_data.split('.')[-1]
            if exe == 'json':
                with open(input_data, mode='r') as f:
                    df_dict = json.load(f)
            elif exe == 'csv':
                input_data = pd.read_csv(input_data, **kwargs)
            elif (exe == 'pickle')|(exe == 'pkl'):
                input_data = pd.read_pickle(input_data, **kwargs)
            else:
                df_dict = {}
        if isinstance(input_data, pd.DataFrame):
            df_dict = make_config_from_df(input_data)

    except Exception as e:
        df_dict = {}
        import traceback
        traceback.print_exc()
        
    return df_dict
    

def make_df_from_config(dict_config_for_df):
    """
    Generating DataFrame with random values from config (Dict).
    Args:
        dict_config_for_df (Dict) : config data
    Returms:
        df  (pd.DataFrame)
    """
    num_rows = dict_config_for_df['num_rows']
    df = pd.DataFrame()
    dict_features = dict_config_for_df['features']

    # make each feature
    for feature_name in dict_features.keys():
        features = []
        nan_rate = dict_features[feature_name]['NaN rate']
        dtype = dict_features[feature_name]['Dtype']
        white_space = False
        if dtype=='str':
            white_space = dict_features[feature_name]['NaN to white space']
            unique = dict_features[feature_name]['Unique']
            if unique=="Random letter":
                for i in range(num_rows):
                    random_list = [random.choice(string.ascii_lowercase) for n in range(dict_features[feature_name]['Char digits'])]
                    features.append("".join(random_list))
            elif unique=="Random number":
                for i in range(num_rows):
                    random_int = random.randint(dict_features[feature_name]['Min'], dict_features[feature_name]['Max'])
                    features.append(str(random_int).zfill(dict_features[feature_name]['Char digits']))
            elif unique=="Unique Seaquential number":
                start = dict_features[feature_name]['Start']
                features = [
                    str(i).zfill(dict_features[feature_name]['Char digits'])
                    for i in range(start, start+num_rows)
                ]
            elif unique=="Unique letter":
                for i in range(num_rows):
                    random_list = [random.choice(string.ascii_lowercase) for n in range(dict_features[feature_name]['Char digits']-len(str(i)))]
                    random_list.append(str(i))
                    features.append("".join(random_list))
            elif unique=="yourself":
                features = random.choices(dict_features[feature_name]['Unique list'].split(','), k=num_rows)
            features = np.array(features)
        elif dtype=='int':
            for i in range(num_rows):
                random_int = random.randint(dict_features[feature_name]['Min'], dict_features[feature_name]['Max'])
                features.append(random_int)
            features = np.array(features)
            if nan_rate!=0:
                print(f'On the int column "{features}", np.nan are detected. This column is converted to float.')
                features = features.astype(float)
        elif dtype=='float':
            for i in range(num_rows):
                random_int = random.uniform(dict_features[feature_name]['Min'], dict_features[feature_name]['Max'])
                features.append(random_int)
            features = np.array(features)
        elif dtype=='datetime':
            freq = dict_features[feature_name]['Freq'][0]
            date = pd.date_range(start=dict_features[feature_name]['Start'], end=dict_features[feature_name]['End'], freq=freq)
            date = np.tile(date.values, num_rows//len(date)+1) # Any missing lines are repeated
            features = date[:num_rows]
        
        df[feature_name] = features

        if nan_rate!=0:
            nan_idx = random.sample(range(num_rows), round(num_rows*nan_rate))
            if white_space:
                df.loc[nan_idx, feature_name] = " "
                white_space = False
            else:
                df.loc[nan_idx, feature_name] = np.nan
    return df


def make_config_from_df(
    df,
):
    """
    Generate config from DataFrame.
    Args:
        df (pd.DataFrame)
    Returns:
        dict_config_for_df (Dict) : config data
    """

    dict_config_for_df = {}
    dict_config_for_df['df_name'] = 'test_df'
    dict_config_for_df['num_rows'] = len(df)
    dict_config_for_df['features'] = {}

    for col in df.columns:
        dict_config_for_df['features'][col] = {}
        dict_config_for_df['features'][col]['NaN rate'] = df[col].isnull().sum()/len(df)
        if 'int' in str(df[col].dtype):
            dict_config_for_df['features'][col]['Dtype'] = 'int'
            dict_config_for_df['features'][col]['Max'] = df[col].max()
            dict_config_for_df['features'][col]['Min'] = df[col].min()
        elif 'float' in str(df[col].dtype):
            if all(df[col].dropna().apply(lambda x: x.is_integer())):
                dict_config_for_df['features'][col]['Dtype'] = 'int'
            else:
                dict_config_for_df['features'][col]['Dtype'] = 'float'
            dict_config_for_df['features'][col]['Max'] = df[col].max()
            dict_config_for_df['features'][col]['Min'] = df[col].min()
        elif 'datetime' in str(df[col].dtype):
            dict_config_for_df['features'][col]['Dtype'] = 'datetime'
            dict_config_for_df['features'][col]['Start'] = df[col].min().strftime('%Y/%m/%d')
            dict_config_for_df['features'][col]['End'] = df[col].max().strftime('%Y/%m/%d')
            if df[col].dt.day.nunique()!=1:
                freq = "Daily"
            elif df[col].dt.month.nunique()!=1:
                freq = "Monthly"
            else:
                freq = "Yearly"
            dict_config_for_df['features'][col]['Freq'] = freq            
        else:
            dict_config_for_df['features'][col]['Dtype'] = 'str'
            df_col = df[col].dropna().astype(str).copy()
            dict_config_for_df['features'][col]['NaN to white space'] = False
            if dict_config_for_df['features'][col]['NaN rate'] == 0:
                dict_config_for_df['features'][col]['NaN rate'] = (df_col.str.contains('^\s+$', regex=True)).sum()/len(df) # space is NaN
                if dict_config_for_df['features'][col]['NaN rate'] > 0:
                    dict_config_for_df['features'][col]['NaN to white space'] = True
                    df_col = df[~df_col.str.contains('^\s+$', regex=True)][col]
            if all(df_col.str.isdigit())&(len(df_col)!=0):
                if df_col.nunique()==len(df_col):
                    dict_config_for_df['features'][col]['Unique'] = 'Unique Seaquential number'
                    dict_config_for_df['features'][col]['Start'] = df_col.astype(float).min()
                    dict_config_for_df['features'][col]['Char digits'] = df_col.apply(len).max()
                else:
                    dict_config_for_df['features'][col]['Unique'] = 'Random number'
                    dict_config_for_df['features'][col]['Max'] = df_col.astype(float).max()
                    dict_config_for_df['features'][col]['Min'] = df_col.astype(float).min()
                    dict_config_for_df['features'][col]['Char digits'] = df_col.apply(len).max()
            elif df_col.nunique() <= 50:
                unique = df_col.unique()
                if len(unique) == 0:
                    unique = [" "]
                dict_config_for_df['features'][col]['Unique'] = 'yourself'
                dict_config_for_df['features'][col]['Unique list'] = ','.join(unique)
            else:
                if df_col.nunique()==len(df_col):
                    dict_config_for_df['features'][col]['Unique'] = 'Unique letter'
                    dict_config_for_df['features'][col]['Char digits'] = df_col.apply(len).max()
                else:
                    dict_config_for_df['features'][col]['Unique'] = 'Random letter'
                    dict_config_for_df['features'][col]['Char digits'] = df_col.apply(len).max()
    return dict_config_for_df