import pandas as pd

@derived
def get_screened(selected):
    return pd.DataFrame([[1],[2]],columns=['ptid'])

@derived
def get_dropped(selected:pd.DataFrame,
                 screened:pd.DataFrame):
    return pd.DataFrame([[2],[3],],columns=['ptid'])

@derived
def get_enrolled(selected:pd.DataFrame,
                 screened:pd.DataFrame):
    res=pd.merge(selected,screened,on='ptid')
    logger.info(f"res:{res}")
    return res

@derived
def get_dropped(selected:pd.DataFrame,
                 enrolled:pd.DataFrame):
    res=selected[~selected['ptid'].isin(enrolled['ptid'])]
    logger.info(f"res:{res}")
    return res


def test_child_tree():
    c0= Spiredf('selected',pd.DataFrame([[1],[2],[3],[4]],columns=['ptid']))
    c1= Spiredf('enrolled',pd.DataFrame([[1],],columns=['ptid']))
    #c2= Spiredf('screened',pd.DataFrame([[1],[2]],columns=['ptid']))
    c3= Spiredf('outlier',pd.DataFrame([[4],],columns=['ptid']))
    c4= Spiredf('excluded',pd.DataFrame([[2],],columns=['ptid']))
    c5= Spiredf('dropped',pd.DataFrame([[2],[3],],columns=['ptid']))
    Spiredf.find_all_children()
    return c0.draw_child_tree()

def test_parent_tree():
    c0= Spiredf('selected',pd.DataFrame([[1],[2],[3],[4]],columns=['ptid']))
    #c2= Spiredf('screened',pd.DataFrame([[1],[2]],columns=['ptid']))
    c3= Spiredf('outlier',pd.DataFrame([[4],],columns=['ptid']))
    c4= Spiredf('excluded',pd.DataFrame([[2],],columns=['ptid']))
    get_enrolled()
    get_dropped()
    return Spiredf.get('enrolled').draw_parent_tree()
