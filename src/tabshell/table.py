from spire.spire import Spiredf,derived
from .tables_helper import series_type,get_num_uniq_pts
import pandas as pd
import numpy as np
from loguru import logger
import sys
class Table():
    def __init__(self,name,columns=[],rows=[]):
        self.columns=columns#CohortNames
        self.rows=rows#variable expressions
        self.format="_.2f"
        for c in columns:
            try: 
                Spiredf.get(c)
            except Exception  as e:
                raise Exception(f"Spriredf {c} not found in {list(Spiredf.instances.keys())}",e)
    
    def compute_tab(self):
        arr=[]
        for c in self.columns:
            _row=[]
            for r in self.rows:
                _row.append(self.compute_cell_tab(c,r))
            col_df=pd.concat(_row).set_index(['var_name','var_value','stat','dtype']).rename(columns={'value':c})
            #col_df.columns=pd.MultiIndex.from_product([[c],list(col_df.columns)])
            arr.append(col_df)
        return pd.concat( arr, axis=1)
    
    def compute_fig(self):
        arr=[]
        for c in self.columns:
            _row=[]
            for r in self.rows:
                _row.append(self.compute_cell_fig(c,r))
            col_df=pd.concat(_row)
            col_df.columns=pd.MultiIndex.from_product([[c],list(col_df.columns)])
            arr.append(col_df)
        return pd.concat(arr,axis=1)

    
    def compute_cell_tab(self,c,r):
        '''returns df of rows each having
        org row_name and stat index columns, followed by value'''
        try:
            logger.trace(f"compute cell {c}{r}")
            
            df=Spiredf.get(c).df[[r,Spiredf.ptid]]
            s=df[r]
            logger.debug(f"{s.value_counts(dropna=False)}")

            res=None
            match series_type(s):
                case 'boolean':
                    res= compute_boolean_tab(r,df)
                case 'numeric':
                    res= compute_numeric_tab(r,df)
                case 'string':
                    res= compute_string_tab(r,df)
                case _:
                    raise Exception(f"Unknown type : {s.value_counts()}")

            res['value']=res['value'].apply(lambda x:f"{x:{self.format}}" if isinstance(x,float) else x )
            res['value']=res['value'].apply(lambda x:"0" if x==f"{0:{self.format}}" else x )
            res['value']=res.apply(lambda r: r['value'].split('.')[0] if (('count' in r['stat']) and (pd.notna(r['value']))) else (r['value'] ),axis=1) #for integer counts
        except Exception as e:
            logger.error(f"{e} {str(e)} {list(Spiredf.get(c).df.columns)}")
            return pd.DataFrame([[r,'','error',e]],columns=['var_name','var_value','stat','value'])
        return res
    

def compute_boolean_tab(name,df):
    arr=[]
    s=df[name]
    vc=s.value_counts()
    nadf=df[pd.isna(df[name])]

    arr.append([name,'*','count',len(df)])
    arr.append([name,'*','count_uniqpt',get_num_uniq_pts(df)])
    arr.append([name,'*','micro_mean_count',np.mean(df[Spiredf.ptid].value_counts())])
    arr.append([name,'*','micro_median_count',np.median(df[Spiredf.ptid].value_counts())])
    for k in vc.keys():
        _df=df[df[name]==k].copy()
        arr.extend(compute_boolean_tab_template(name,k,_df,df))     
    arr.extend(compute_boolean_tab_template(name,'na',nadf,df))
    res=pd.DataFrame(arr,columns=['var_name','var_value','stat','value'])
    res['dtype']='boolean'
    return res

def compute_boolean_tab_template(name,value_key,subset,fullset):
    arr=[]
    arr.append([name,f"{name}:{value_key}",'count',len(subset)])
    arr.append([name,f"{name}:{value_key}",'prop',len(subset)/len(fullset)])
    arr.append([name,f"{name}:{value_key}",'prop_uniqpt',get_num_uniq_pts(subset)/get_num_uniq_pts(fullset)])
    arr.append([name,f"{name}:{value_key}",'count_uniqpt',get_num_uniq_pts(subset)])
    arr.append([name,f"{name}:{value_key}",'micro_mean_count',np.mean(subset[Spiredf.ptid].value_counts())])
    arr.append([name,f"{name}:{value_key}",'micro_median_count',np.median(subset[Spiredf.ptid].value_counts())])
    return arr

def compute_numeric_tab(name,df):
    arr=[]
    s=df[name]
    nadf=df[pd.isna(df[name])]
    arr.append([name,f"{name}",'uniqpt not na',get_num_uniq_pts(df[pd.notna(s)])])
    arr.append([name,f"{name}",'count',len(s)])
    arr.append([name,f"{name}",'mean',np.mean(s)])
    arr.append([name,f"{name}",'median',np.median(s)])
    arr.append([name,f"{name}",'uniqpt pts na',nadf[Spiredf.ptid].nunique()])
    arr.append([name,f"{name}",'na',len(nadf)])
    
    res=pd.DataFrame(arr,columns=['var_name','var_value','stat','value'])
    res['dtype']='numeric'
    return res

def compute_string_tab(name,df):
    arr=[]
    s=df[name]
    vc=s.value_counts(dropna=True)
    logger.debug(f"vc:{vc.index.astype(str)}")
    for k in vc.index.astype(str):
        _df=df[df[name]==k]
        arr.append([name,f"{name}:{k}",'uniqpt',_df[Spiredf.ptid].nunique()])
        arr.append([name,f"{name}:{k}",'count',len(_df)])
    res=pd.DataFrame(arr,columns=['var_name','var_value','stat','value'])
    res['dtype']='string'
    return res



#.first .last .mean  at patient level
# row_sub_name (var:value:stat) 
#consolidated exp for boolean var:True:count / var::count (var:True:prop) (var:na:prop)