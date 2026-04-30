#!pip3 install openpyxl
#%%

import pandas as pd
from loguru import logger
from spire.spire import Spiredf
import glob
from pathlib import Path

class TableRow():

    def __init__(self,exp):
        #human_name:[query].statistic_expression
        self.human_name

class TableDefinition():
    instances={}

    def __init__(self,name,rows,cols,paths):
        self.name=name
        self.cols=cols
        self.rows=rows
        self.paths=paths
        TableDefinition.instances[name]=self
        logger.debug(f"name:{name} \n\nrows:\n{rows} \n\ncols:\n{cols} \n\npaths:\n{len(paths)}")

    @classmethod
    def get(cls,name):
        return TableDefinition.instances[name]
    
    def __str__(self):
        str= f"{self.name} \ncols:{list(self.cols.iloc[0:0,])}  \nrows:"
        for x in ['var_name','path', 'statistic']:
            str+= f"\n\t {x} {list(self.rows[x])}"
            #\nrows: \n\n varname{list(self.rows['var_name'])}
        return str
    
    @classmethod
    def table_definitions_from_dir(cls,file_path):
        paths=pd.read_csv(f"{file_path}/paths.csv")['path'].tolist()
        for tab_path in glob.glob(f"{file_path}/*"):
            tab_name = Path(tab_path).name
            if 'path' not in tab_name:
                logger.debug(f"tab_name:{tab_name}")
                rdf=pd.read_csv(f"{file_path}/{tab_name}/rows.csv",)
                cdf=pd.read_csv(f"{file_path}/{tab_name}/cols.csv")
                cols=cdf.iloc[:,0:2].map(lambda x:str(x).strip())
                rows=rdf.iloc[:,0:3].map(lambda x:str(x).strip())
                TableDefinition(tab_name,rows,cols,paths)

    @classmethod
    def table_definitions_from_excel(cls,file_path):
        xls = pd.ExcelFile(file_path,engine="openpyxl")
        raise Exception('TODO')
    
    def compute_tab(self):
        arr=[]
        
        for idx,r in self.rows.iterrows():
            var_name,path,statistic=r['var_name'],r['path'],r['statistic']
            _row=[var_name,path,statistic]
            for c in self.cols['cohort']:      
                try:
                    slice=Spiredf.get(c).df
                    if pd.notna(path) and path!='nan':
                        slice=slice.query(path)
                    logger.debug(f"{c} {var_name} {len(slice)}")
                    value=self.compute_cell_tab(c,r,df=slice)
                    _row.append( value)
                except Exception as e:
                    logger.error(e)
                    _row.append('E')

            arr.append(_row)
        
        t=pd.DataFrame(arr,columns=['var_name','path','statistic']+list(self.cols['cohort']))
        return t
    
    def compute_cell_tab(self,c,r,df):
        logger.debug(f"r['statistic']:{r['statistic']}")        
        stat = r["statistic"]

        match stat:
            case "count_unique_pts":
                return df[Spiredf.ptid].nunique()
            case "count_rows":
                return len(df)
            case "micro_mean":
                return df.value_as_number.mean()
            case "macro_mean":
                return df.groupby(Spiredf.ptid).value_as_number.mean().mean()
            case _:
                raise ValueError(f"Unknown statistic: {stat}")



# %%
