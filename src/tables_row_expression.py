#!pip3 install openpyxl
#%%

import pandas as pd
from loguru import logger
from .cohort import Spiredf

class TableRow():

    def __init__(self,exp):
        #human_name:[query].statistic_expression
        self.human_name

class TableDefinition():
    instances={}

    def __init__(self,name,rows,cols):
        self.name=name
        self.cols=cols
        self.rows=rows
        logger.debug(f"name:{name} \n\nrows:\n{rows} \n\ncols:\n{cols}")

    @classmethod
    def get(cls,name):
        return TableDefinition.instances[name]
    
    def __str__(self):
        str= f"{self.name} \ncols:{list(self.cols.iloc[0:0,])}  \nrows:"
        for x in ['var_name','filter', 'statistic']:
            str+= f"\n\t {x} {list(self.rows[x])}"
            #\nrows: \n\n varname{list(self.rows['var_name'])}
        return str
    
    @classmethod
    def read_table_definitions(cls,file_path):
        xls = pd.ExcelFile(file_path,engine="openpyxl")
        for sheet_name in xls.sheet_names:
            df=pd.read_excel(file_path,sheet_name=sheet_name)
            cols=df.iloc[0:0,3:].map(lambda x:str(x).strip())
            rows=df.iloc[:,0:3].map(lambda x:str(x).strip())
            TableDefinition.instances[sheet_name]=TableDefinition(sheet_name,rows,cols)

    def compute_tab(self):
        arr=[]
        
        for idx,r in self.rows.iterrows():
            var_name,filter,statistic=r['var_name'],r['filter'],r['statistic']
            _row=[var_name,filter,statistic]
            for c in self.cols:      
                try:
                    slice=Spiredf.get(c).df
                    if pd.notna(filter) and filter!='nan':
                        slice=slice.query(filter)
                    logger.debug(f"{c} {var_name} {len(slice)}")
                    value=self.compute_cell_tab(c,r,df=slice)
                    _row.append( value)
                except Exception as e:
                    logger.error(e)
                    _row.append('E')

            arr.append(_row)
        
        t=pd.DataFrame(arr,columns=['var_name','filter','statistic']+list(self.cols))
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

# %%
