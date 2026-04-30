#%%
#%reload_ext autoreload
#%autoreload 2
import unittest
from types import SimpleNamespace

import pandas as pd
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
import tabshell.tables_row_expression as tre
import glob
tab=None

#%%



class FakeSpiredf:
    ptid = "patient_id"
    registry = {}

    @classmethod
    def get(cls, name):
        return cls.registry[name]


class TestHello(unittest.TestCase):
    def test_hello(self):
        self.assertEqual("Hello, World!", "Hello, World!")


class TestTableDefinition(unittest.TestCase):
    def setUp(self):
        self.original_spiredf = tre.Spiredf
        self.original_instances = dict(tre.TableDefinition.instances)

        tre.Spiredf = FakeSpiredf
        tre.TableDefinition.instances = {}

        FakeSpiredf.registry = {
            "screened": SimpleNamespace(
                df=pd.DataFrame(
                    {
                        "patient_id": [1, 1, 2, 3],
                        "value_as_number": [10.0, 20.0, 30.0, 40.0],
                        "t2d_icd": [True, False, True, True],
                        "hba1c_order": [True, True, False, True],
                        "metformin_rxnorm": [True, True, False, False],
                        "hba1c_loinc": [True, True, False, False],
                    }
                )
            ),
            "selected": SimpleNamespace(
                df=pd.DataFrame(
                    {
                        "patient_id": [1, 2],
                        "value_as_number": [100.0, 200.0],
                        "t2d_icd": [True, False],
                        "hba1c_order": [True, False],
                        "metformin_rxnorm": [True, False],
                        "hba1c_loinc": [True, False],

                    }
                )
            ),
        }

    def tearDown(self):
        tre.Spiredf = self.original_spiredf
        tre.TableDefinition.instances = self.original_instances

    def test_get_returns_registered_instance(self):
        file_path='/home/dev/code/tabshelldev/tests/tabshell/resources/test1/table_defn'
        tre.TableDefinition.table_definitions_from_dir(file_path)
        tab=tre.TableDefinition.get('t2d_tab1')
        logger.debug(tab.compute_tab())
        self.assertIsInstance(tre.TableDefinition.get('t2d_tab1'), tre.TableDefinition)


if __name__ == "__main__":
    # notebook-safe: avoids ipykernel argv (-f ...) parsing errors
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
# %%
