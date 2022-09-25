import numpy as np
import pandas as pd
import random
import string
import json
import ipywidgets as iw

from IPython.display import display
from datetime import datetime as dt
from make_df import make_df_from_config

output = iw.Output(layout={'border': '1px solid black'})


def pop_n_widgets(box, n):
    """
    Pop n-th widget from box.

    Args:
        box (iw.Box): ipywidgets box.
        n (int): n-th children
    """
    widgets = list(box.children)
    pop_w = widgets.pop(n)
    box.children = tuple(widgets)
    return pop_w


def str_unique_setting(feature, unique):
    """
    Widgets for each str unique.

    Args:
        feature (iw.Box): ipywidgets box.
        unique (str): kind of unique.
    """
    unique_widgets = []
    if unique == 'Random letter':
        unique_widgets.append(
            iw.BoundedIntText(
                value=8,
                min=1,
                max=10,
                step=1,
                description='Char digits',
                disabled=False,
            )
        )
    elif unique == 'Random number':
        unique_widgets.append(
            iw.BoundedIntText(
                value=8,
                min=1,
                max=10,
                step=1,
                description='Char digits',
                disabled=False,
            )
        )
        unique_widgets.append(
            iw.IntText(
                step=1,
                description='Max',
                disabled=False
            )
        )
        unique_widgets.append(
            iw.IntText(
                step=1,
                description='Min',
                disabled=False
            )
        )
    elif unique == 'Seaquential number':
        unique_widgets.append(
            iw.BoundedIntText(
                value=8,
                min=1,
                max=10,
                step=1,
                description='Char digits',
                disabled=False,
            )
        )
        unique_widgets.append(
            iw.IntText(
                step=1,
                description='Start',
                disabled=False
            )
        )
    elif unique == 'yourself':
        unique_widgets.append(
            iw.Text(
                description='Unique list',
                value='',
                placeholder='aaa,bbb,ccc,..(*No space)',
            )
        )
    feature.children += tuple(unique_widgets)


def str_setting(feature):
    """
    Str widgets setting

    Args:
        feature (iw.Box): ipywidgets box.
    """
    unique = iw.Dropdown(
        description="Unique",
        options = ["Random letter", "Random number", "Seaquential number", "yourself"],
        value=None,
    )
    def on_value_change(change) -> None:
        if change['name'] == 'value':
            while len(feature.children)>=5:
                pop_n_widgets(feature, -1)
            str_unique_setting(feature, change['new'])
    
    unique.observe(on_value_change, names='value')
    feature.children += (unique,)

    
def int_setting(feature):
    """
    Int widgets setting

    Args:
        feature (iw.Box): ipywidgets box.
    """
    int_max = iw.IntText(
        step=1,
        description='Max',
        disabled=False,
        value=10
    )
    int_min = iw.IntText(
        step=1,
        description='Min',
        disabled=False,
        value=0,
    )
    feature.children += (int_max, int_min)


def float_setting(feature):
    """
    Float widgets setting

    Args:
        feature (iw.Box): ipywidgets box.
    """
    float_max = iw.FloatText(
        step=0.01,
        description='Max',
        disabled=False,
        value=1.0,
    )
    float_min = iw.FloatText(
        step=0.01,
        description='Min',
        disabled=False,
        value=0.0,
    )
    feature.children += (float_max, float_min)


def datetime_setting(feature):
    """
    Datetime widgets setting

    Args:
        feature (iw.Box): ipywidgets box.
    """
    dt_start = iw.Text(
        description='Start',
        value='',
        placeholder='YYYY/MM/DD',
    )
    dt_end = iw.Text(
        description='End',
        value='',
        placeholder='YYYY/MM/DD',
    )
    freq = iw.Dropdown(
        description="Freq",
        options = ["Daily", "Monthly", "Yearly"],
        value=None,
    )
    feature.children += (dt_start, dt_end, freq)

                     
def dtype_setting(feature, dtype):
    """
    Dtypes selection

    Args:
        feature (iw.Box): ipywidgets box.
        dtype (str): dtype.
    """
    if dtype=="str":
        str_setting(feature)
    elif dtype=='int':
        int_setting(feature)
    elif dtype=='float':
        float_setting(feature)
    elif dtype=='datetime':
        datetime_setting(feature)
        


class DFWidgets(object):    
    def __init__(self, df_config={}, lim_w=4):
        self.headers, self.features = self.make_df_widgets(df_config)
        self.lim_w = lim_w #横方向の表示の最大件数
        
        self.features_widgets = iw.VBox()
        
    
    def make_df_widgets(self, df_config={}):
        """
        df_config(Dict)を受け取りその内容をもとにwidgets GUIを作成する.

        Args:
            df_config (Dict[str, str]): dfを作成するための情報
        """
        headers = []
        features = []
        
        headers = self.make_header_widgets(df_config.get('df_name'), df_config.get('num_rows'))
        
        if df_config.get('features') is not None:
            for i in range(len(df_config.get('features'))):
                features.append(self.make_feature_widgets())
            features = self.feature_setting(features, df_config.get('features'))
        else:
            features.append(self.make_feature_widgets())
        return headers, features
            
        
    def make_header_widgets(self, df_name=None, num_rows=None):
        header = iw.VBox()
        make_df_button = iw.Button(description='make DF')
        df_name = iw.Text(
            description='DF Name',
            value='test_df' if df_name is None else df_name,
        )
        num_rows = iw.BoundedIntText(
            value=100 if num_rows is None else num_rows,
            min=0,
            max=1e8,
            step=1,
            description='Num Rows',
            disabled=False,
        )
        def on_click_make_df(clicked_button: iw.Button) -> None:
            df_dict, df = self.make_df(self.headers, self.features)
            with open(f'{df_name.value}.json', mode='w') as f:
                json.dump(df_dict, f, indent=2, ensure_ascii=False)
            df.to_pickle(f'{df_name.value}.pkl')
                
        make_df_button.on_click(on_click_make_df)
        header.children += (make_df_button, df_name, num_rows)
        return header
    
    
    def make_feature_widgets(self):
        feature = iw.VBox(layout=iw.Layout(border='1px solid #C8C8C8'))
        
        featurename = iw.Text(
            description='Feat Name',
            value='',
            layout=iw.Layout(width='90%')
        )
        delete_button = iw.Button(description='×', layout=iw.Layout(width='10%'))
        featurename = iw.Box([featurename, delete_button])
        
        nan_rate = iw.BoundedFloatText(
            step=0.01,
            value=0.0,
            max=1.0,
            min=0.0,
            description='NaN rate',
            disabled=False
        )
        dtype = iw.Dropdown(
            description="Dtype",
            options = ["str", "int", "float", "datetime"],
            value=None,
        )
        def on_value_change(change) -> None:
            if change['name'] == 'value':
                while len(feature.children)>=4:
                    pop_n_widgets(feature, -1)
                dtype_setting(feature, change['new'])
                
        def on_click_delete(clicked_button: iw.Button) -> None:
            self.features.remove(feature)
            self.show_features()

        dtype.observe(on_value_change, names='value')
        delete_button.on_click(on_click_delete)

        feature.children += (featurename, nan_rate, dtype)
        return feature
    
    
    def feature_setting(self, features, features_conf):
        for feat, feat_name in zip(features, features_conf.keys()):
            feat.children[0].children[0].value = feat_name
            for i, v in enumerate(features_conf[feat_name].values(), 1):
                feat.children[i].value = v
        return features
    
    
    def show(self):
        self.show_header()
        self.show_features()
        
        
    def show_header(self):
        display(self.headers)
        
    
    def show_features(self):
        add_button = iw.Button(description='+')
        features = self.make_features(self.features, add_button, self.lim_w)
    
        self.features_widgets.children = tuple(features)
        
        def on_click(clicked_button: iw.Button) -> None:
            self.features.append(self.make_feature_widgets())
            features = self.make_features(self.features, add_button, self.lim_w)
            self.features_widgets.children = tuple(features)

        add_button.on_click(on_click)
        display(self.features_widgets)
        
        
    
    def make_features(self, features, add_button, lim_w):
        features = [iw.Box(features[idx:idx + lim_w]) for idx in range(0,len(features), lim_w)] # divide by lim_w
        if len(features[-1].children) == 4:
            features.append(iw.Box([add_button]))
        else:
            features[-1].children += (add_button,)
        return features

    
    def make_df(self, headers, features):
        df_config = {
            'df_name':headers.children[1].value,
            'num_rows':headers.children[2].value,
            'features':{},
        }
        
        for feature in features:
            feature_name = feature.children[0].children[0].value
            df_config['features'][feature_name] = {}
            for feat in feature.children[1:]:
                df_config['features'][feature_name][feat.description] = feat.value
        return df_config, make_df_from_config(df_config)
