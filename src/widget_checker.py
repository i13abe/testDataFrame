import ipywidgets as iw

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


def is_not_in(widget, in_list, init_layout=iw.Layout()):
    """
    Check not in in_list of widget value.
    If not in, return True
    """
    if (widget.value == "")|(widget.value is None):
        return False # empty is False
    widget.layout = init_layout
    if widget.value in in_list:
        print(f"{widget.value} is duplicated.")
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
    - feature names are not duplicated. If unique, return True
    If all checks of list are True, return True
    """
    flag = True
    # header check
    for i in [1, 2]:
        flag &= is_not_empty(headers.children[i])

    # feature check
    list_feature_name = []
    for feature in features:
        flag &= is_not_empty(feature.children[0].children[0], iw.Layout(width="90%")) # for FeatName
        for feature_detail in feature.children[1:]:
            flag &= is_not_empty(feature_detail)
        dtype = feature.children[2].value
        if (dtype=="int")|(dtype=="float"):
            flag &= min_max_check(feature.children[4], feature.children[3])
        flag &= is_not_in(feature.children[0].children[0], list_feature_name, iw.Layout(width="90%")) # feature names duplication check
        list_feature_name.append(feature.children[0].children[0].value)
    return flag