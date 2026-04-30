import pandas as pd
import numpy as np
from .cohort import Spiredf,derived
from .table import Table
from loguru import logger
from .tables_helper import series_type

def get_hist(datasets,labels,title):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    #datasets = [data1, data2, data3]
    #labels = ["A", "B", "C"]

    for d, label in zip(datasets, labels):
        ax.hist(d, bins=30, alpha=0.4, label=label)

    ax.set_title(title)
    ax.legend()
    #plt.show()
    return plt

def get_bar_chart_of_proportions(data,variables,groups,title):
    import numpy as np
    import matplotlib.pyplot as plt

    # Groups on x-axis
    #groups = ["Group A", "Group B", "Group C",'GROUP D']

    # Conditions within each group
    #variables = ["V 1", "V 2", "V 3"]

    # Data: rows = groups, columns = conditions
    data1 = np.array([
        [0.12, 0.10, 0.08],
        [0.11, 0.09, 0.07],
        [0.14, 0.12, 0.10],
        [0.2, 0.4, 0.6],
    ])
    data= np.array(data)

    x = np.arange(len(variables))              # group positions
    width = 0.8 / len(groups)           # total width split across conditions

    fig, ax = plt.subplots()

    for i, cond in enumerate(groups):
        bars=ax.bar(
            x + i*width - width*(len(groups)-1)/2,
            data[:, i],
            width,
            label=cond
        )
        ax.bar_label(bars, fmt="%.3f", padding=2)
    
    ax.set_xticks(x)
    ax.set_xticklabels(variables)
    ax.set_ylabel("Proportion")
    ax.set_title(title)
    ax.legend()

    return plt

def compute_boolean_fig(tab):
    
    cohs=tab.columns
    cohort1=cohs[0]
    tab1=tab[tab.index.to_frame()['dtype']=='boolean']
    sel_var_names=list(set(tab1.index.to_frame()['var_name']))
    
    title=f"Proportion of unique patients with a true fact"
    logger.debug(f"sel_var_names:{sel_var_names}")
    arr=[]
    data=[]
    for var_name in sel_var_names:
        _data=[]
        for coh in cohs:
            df=Spiredf.get(coh).df
            prop=df[df[var_name]==True][Spiredf.ptid].nunique()/df[Spiredf.ptid].nunique()
            _data.append(prop)
        data.append(_data)
    logger.debug(f"bar_chart_of_proportions:{data}")
    fig=get_bar_chart_of_proportions(data,sel_var_names,cohs,title=title)
    arr.append(fig)
        
    return arr




def compute_cell_fig(self,c,r):
    '''returns df of rows each having
    org row_name and stat index columns, followed by png'''
    logger.trace(f"compute cell figure {c}{r}")
    s=Spiredf.get(c).df[r]
    df=Spiredf.get(c).df[[r,Spiredf.ptid]]
    logger.debug(f"{s.value_counts(dropna=False)}")

    res=None
    match series_type(s):
        case 'boolean':
            pass#res= compute_boolean_fig(r,c,df)
        case 'numeric':
            pass#res= compute_numeric_fig(r,c,df)
        case 'string':
            pass#res= compute_string_fig(r,c,df)
        case _:
            raise Exception(f"Unknown type : {s.value_counts()}")
    return res




