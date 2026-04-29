#%%
#%reload_ext autoreload
#%autoreload 2

import pandas as pd
from loguru import logger
import sys,json
from pathlib import Path
class Spiredf():
    instances={}
    find_counter=0
    ptid='ptid'


    @classmethod
    def set_config(cls,ptid='ptid'):
        cls.ptid=ptid
        cls.stage_dir='/tmp/sprire/spiredf/'

    def __init__(self,name=None,df: pd.DataFrame=None ):
        name=name.lower()
        logger.info(f"init {name}")
        if name is None:
            raise Exception(f"name argument in mandatory")
        if df is None:
            raise Exception(f"df argument in mandatory")
        if name in Spiredf.instances:
            raise Exception(f"Spiredf named {name} is already present in {Spiredf.instances.keys()}")
        #if not Spiredf.ptid in df.columns:
        #    raise Exception(f"df is missing ptid:{Spiredf.ptid} columns")
        self.name=name
        Spiredf.instances[name]=self #f"{Spiredf.stage_dir}/name/df.parquet"
        self.df=df
        self.df.columns=[x.lower() for x in self.df.columns]
        self.children=[]#immediate children
        self.parents=[]
        logger.info(f" after init {name} Spiredf.instances: {list(Spiredf.instances.keys())}")

    @classmethod
    def reset(cls,name=None):
        
        if name is None:
            logger.info(f"Reset Spiredf for all sdf")
            for x in Spiredf.instances:
                del(Spiredf.instances[x])
        else:
            name=name.lower()
            if name in Spiredf.instances:
                logger.info(f"Reset Spiredf for {name}")
                del Spiredf.instances[name]
            else:
                logger.debug(f"{name} not found in Spiredf.instances {list(Spiredf.instances)} ")
        
    @classmethod
    def get(cls,name):
        name=name.lower()
        logger.info(f"looking for name:{name} in {list(Spiredf.instances.keys())}")
        if not name in Spiredf.instances.keys():
            curr_module=sys.modules.get("__main__")
            all_funcs = []
           
            for mod in list(sys.modules.values()).copy():
                if mod is None:
                    continue
                try:
                    all_funcs.extend(inspect.getmembers(mod, inspect.isfunction))
                except Exception as e:
                    pass

            for f in all_funcs:
                if f[0].startswith('get_') and\
                    f[0].lower()==f"get_{name}".lower():
                    logger.info(f"from get calling func: {f[0]}")
                    f[1]()
                    break
        
        return Spiredf.instances.get(name)

    def __str__(self):
        d= {'name':f"{self.name}",'ptids':f"{set(self.df[Spiredf.ptid])}"}
        d['parents']=[str(x.name) for x in self.parents]
        d['children']=[str(x.name) for x in self.children]
        return json.dumps(d,indent=2)
    

import inspect
def derived(func):
    logger.info(f"Decorator called ..deriving from {func.__name__}")
    arg_names= list(inspect.signature(func).parameters.keys())
    logger.info(f"arg_names:{arg_names}")
    def wrapper(*args,**kwargs):
        logger.info(f"Wrapper called ..deriving from {func.__name__}")
        args=[Spiredf.get(p).df for p in arg_names]
        logger.info(f"args:{args}")
        c=Spiredf(func.__name__.replace('get_',''),func (*args,**kwargs))
        c.parents=[Spiredf.get(p) for p in arg_names]

    return wrapper


