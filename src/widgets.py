import numpy as np
import pandas as pd
import random
import string
import json
import ipywidgets as iw
import gc

from IPython.display import display
from datetime import datetime as dt
from .utils import make_df_from_config


def is_not_empty(widget, init_layout=iw.Layout()):
    """
    Check not empty of widget parameter.
    If not empty return True
    """
    widget.layout = init_layout
    if (widget.value == "")|(widget.value is None):
        print(f"'{widget.description}' is requierd. Not empty.")
        widget.layout = iw.Layout(border='2px solid #FF6347') # color to red on empty box
        return False
    return True


def min_max_check(min_widget, max_widget, init_layout=iw.Layout()):
    """
    Check min<=max of int or float feature.
    If min<=max, return True.
    """
    max_widget.layout = init_layout
    min_widget.layout = init_layout
    if float(min_widget.value) > float(max_widget.value):
        print("min must be <=max")
        min_widget.layout = iw.Layout(border='2px solid #FF6347', margin="2px")
        max_widget.layout = iw.Layout(border='2px solid #FF6347', margin="2px")
        return False
    return True


def parameter_check(headers, features):
    """
    Check the parameter of widgets.
    <Check list>
    - is empty or not. If not empty, return True
    - min <= max or not. If min<=max, return True
    If all checks of list are True, return True
    """
    flag = True
    # header check
    for i in [1, 2]:
        flag &= is_not_empty(headers.children[i])

    # feature check
    for feature in features:
        flag &= is_not_empty(feature.children[0].children[0], iw.Layout(width="90%")) # for FeatName
        for feature_detail in feature.children[1:]:
            flag &= is_not_empty(feature_detail)
        dtype = feature.children[2].value
        if (dtype=="int")|(dtype=="float"):
            flag &= min_max_check(feature.children[4], feature.children[3])
    return flag


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
            iw.BoundedIntText(
                min=0,
                step=1,
                description='Min',
                disabled=False
            )
        )
    elif unique == 'Unique Seaquential number':
        unique_widgets.append(
            iw.BoundedIntText(
                value=8,
                min=1,
                step=1,
                description='Char digits',
                disabled=False,
            )
        )
        unique_widgets.append(
            iw.BoundedIntText(
                min=0,
                step=1,
                description='Start',
                disabled=False
            )
        )
    elif unique == 'Unique letter':
        unique_widgets.append(
            iw.BoundedIntText(
                value=8,
                min=1,
                step=1,
                description='Char digits',
                disabled=False,
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
    white_space = iw.Checkbox(
        description="NaN to white space",
        value=False,
    )
    unique = iw.Dropdown(
        description="Unique",
        options = ["Random letter", "Random number", "Unique Seaquential number", "Unique letter", "yourself"],
        value=None,
    )
    def on_value_change(change) -> None:
        if change['name'] == 'value':
            while len(feature.children)>=6:
                w = pop_n_widgets(feature, -1)
                del w
                gc.collect()
            str_unique_setting(feature, change['new'])
    
    unique.observe(on_value_change, names='value')
    feature.children += (white_space, unique)

    
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
    def __init__(self, dict_config_for_df={}, lim_w=4):
        self.headers, self.features = self.make_df_widgets(dict_config_for_df)
        self.output = iw.Output(layout={'border': '1px solid black'}) # for std out
        self.lim_w = lim_w # limit of horizontal widgets to show on notebook
        
        self.features_widgets = iw.VBox()
        
    
    def make_df_widgets(self, dict_config_for_df={}):
        """
        Generate GUI from dict_config_for_df(Dict).

        Args:
            dict_config_for_df (Dict[str, str]): config to generate widgets
        """
        headers = []
        features = []
        
        headers = self.make_header_widgets(dict_config_for_df.get('df_name'), dict_config_for_df.get('num_rows'))
        
        if dict_config_for_df.get('features') is not None:
            for i in range(len(dict_config_for_df.get('features'))):
                features.append(self.make_feature_widgets())
            features = self.feature_setting(features, dict_config_for_df.get('features'))
        else:
            features.append(self.make_feature_widgets())
        return headers, features
            
        
    def make_header_widgets(self, df_name=None, num_rows=None):
        """
        Generate an initial header widgets
        Header is constructed "make DF button", "DF Name", and "Num Rows".
        Args:
            df_name (str): DataFrame name. Default to None.
            num_rows (int): The number of rows. Defaults to None.
        """
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
            with self.output:
                self.output.clear_output()
                print(f"processing....", end="")
                if parameter_check(self.headers, self.features):
                    dict_config_for_df = self.get_config_to_make_df(self.headers, self.features)
                    df = self.make_df(dict_config_for_df)
                    with open(f'{df_name.value}.json', mode='w') as f:
                        json.dump(dict_config_for_df, f, indent=2, ensure_ascii=False)
                    df.to_pickle(f'{df_name.value}.pkl')
                    print("Done.")
                    print(f"json saved as {df_name.value}.json. DataFrame saved as {df_name.value}.pkl.")
                else:
                    print(f"Check all missing.")
                
        make_df_button.on_click(on_click_make_df)
        header.children += (make_df_button, df_name, num_rows)
        return header
    
    
    def make_feature_widgets(self):
        """
        Generate an initial feature widgets
        """
        feature = iw.VBox(layout=iw.Layout(border='1px solid #C8C8C8'))
        
        _featurename = iw.Text(
            description='Feat Name',
            value='',
            layout=iw.Layout(width='90%')
        )
        delete_button = iw.Button(description='×', layout=iw.Layout(width='10%'))
        
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
                    w = pop_n_widgets(feature, -1)
                    del w
                    gc.collect()
                dtype_setting(feature, change['new'])
                
        def on_click_delete(clicked_button: iw.Button) -> None:
            self.features.remove(feature)
            gc.collect()
            self.show_features()

        dtype.observe(on_value_change, names='value')
        delete_button.on_click(on_click_delete)

        featurename = iw.Box([_featurename, delete_button])
        feature.children += (featurename, nan_rate, dtype)
        return feature
    
    
    def feature_setting(self, features, dict_config_for_df):
        """
        Set the parameter of features into widgets.
        Args:
            features (List[iw.VBox]) : List of feature widgets
            dict_config_for_df (Dict[str, str]) : Parameter of features
        """
        for feature_widget, feature_name in zip(features, dict_config_for_df.keys()):
            feature_widget.children[0].children[0].value = feature_name # for Feat Name
            for idx in range(len(dict_config_for_df[feature_name])):
                desc = feature_widget.children[idx+1].description # +1 is offset of header
                feature_widget.children[idx+1].value = dict_config_for_df[feature_name][desc]

        return features
    
    
    def show(self):
        """
        show all widgets
        """
        self.show_output()
        self.show_header()
        self.show_features()


    def show_output(self):
        """
        show std out widget
        """
        display(self.output)

        
    def show_header(self):
        """
        show header widgets
        """
        display(self.headers)
        
    
    def show_features(self):
        """
        show features widgets
        """
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
        """
        Make widgets of features to show on notebook.
        Args:
            features (List[iw.VBox()]): List of feature widgets
            add_button (iw.Button()): The button widget for adding a new feature.
            lim_w (int): Limit of horizontal widgets to show on notebook.
        """
        features = [iw.Box(features[idx:idx + lim_w]) for idx in range(0,len(features), lim_w)] # divide by lim_w
        if len(features[-1].children) == lim_w:
            features.append(iw.Box([add_button]))
        else:
            features[-1].children += (add_button,)
        return features

    
    def get_config_to_make_df(self, headers, features):
        """
        Return a dict config from specified parameter of wigets
        """
        dict_config_for_df = {
            'df_name':headers.children[1].value,
            'num_rows':headers.children[2].value,
            'features':{},
        }
        
        for feature in features:
            feature_name = feature.children[0].children[0].value
            dict_config_for_df['features'][feature_name] = {}
            for feature_detail in feature.children[1:]:
                dict_config_for_df['features'][feature_name][feature_detail.description] = feature_detail.value
        return dict_config_for_df


    def make_df(self, dict_config_for_df):
        """
        Make DataFrame from specified parameter
        """
        return make_df_from_config(dict_config_for_df)
