#%%
import sys
from pathlib import Path

# Make src importable
base_dir = Path(__file__).resolve().parent
lib_path = base_dir.parent.parent / "src"
sys.path.insert(0, str(lib_path))

import pandas as pd
from spire.spire import Spiredf, derived
@derived
def get_screened():
    return pd.DataFrame([[1,True], [2,True], [3,False]], columns=["ptid",'t2d_icd'])


@derived
def get_selected(screened: pd.DataFrame):
    return screened[screened['ptid'].isin([2, 3])]   

@derived
def get_enrolled(selected: pd.DataFrame):
    return selected[selected['ptid'].isin([2])]

from tabshell.table import Table


def test_compute_tab_and_export(tmp_path: Path):
    Table(name="demo", columns=["pt"], rows=["age"])

    t2 = Table(
        name="tab_dx",
        columns=["screened", "selected", "enrolled"],
        rows=["t2d_icd"],
    )

    tab = t2.compute_tab()
    assert tab is not None

    out_file = tmp_path / "tab2.xlsx"
    tab.to_excel(out_file, index=False)
    assert out_file.exists()
# %%


t2 = Table(
    name="tab_dx",
    columns=["screened", "selected", "enrolled"],
    rows=["t2d_icd"],
)

t2.compute_tab()
# %%
