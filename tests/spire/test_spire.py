#%%
#%reload_ext autoreload
#%autoreload 2
import sys
from pathlib import Path
import pandas as pd
from loguru import logger

import pandas as pd
import pytest

# Make src importable
base_dir = Path(__file__).resolve().parent
lib_path = base_dir.parent.parent / "src"
sys.path.insert(0, str(lib_path))

from spire.spire import Spiredf, derived


@pytest.fixture(autouse=True)
def _clean_spiredf_state():
    Spiredf.instances.clear()
    Spiredf.find_counter = 0
    Spiredf.ptid = "ptid"
    yield
    Spiredf.instances.clear()


@derived
def get_screened():
    return pd.DataFrame([[1], [2], [3]], columns=["ptid"])


@derived
def get_selected(screened: pd.DataFrame):
    return pd.DataFrame([[2], [3]], columns=["ptid"])


def test_get_calls_matching_get_function_and_creates_instance():
    sdf = Spiredf.get("screened")
    assert sdf is not None
    assert sdf.name == "screened"
    assert list(sdf.df["ptid"]) == [1, 2, 3]


def test_get_resolves_dependency_chain_for_derived():
    selected = Spiredf.get("selected")
    assert selected is not None
    assert selected.name == "selected"
    assert "screened" in Spiredf.instances
    assert [p.name for p in selected.parents] == ["screened"]


def test_init_lowercases_name_and_columns():
    sdf = Spiredf("MyTable", pd.DataFrame([[1]], columns=["PTID"]))
    assert sdf.name == "mytable"
    assert list(sdf.df.columns) == ["ptid"]


def test_duplicate_name_raises():
    Spiredf("screened", pd.DataFrame([[1]], columns=["ptid"]))
    with pytest.raises(Exception, match="already present"):
        Spiredf("screened", pd.DataFrame([[2]], columns=["ptid"]))


def test_get_unknown_name_returns_none():
    assert Spiredf.get("does_not_exist") is None
