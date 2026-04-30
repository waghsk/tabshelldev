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
file_path='/home/dev/code/tabshelldev/tests/tabshell/resources/test1/table_defn'
tre.TableDefinition.table_definitions_from_dir(file_path)
tab=tre.TableDefinition.get('t2d_tab1')
tab.compute_tab()
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
            "cohort_a": SimpleNamespace(
                df=pd.DataFrame(
                    {
                        "patient_id": [1, 1, 2, 3],
                        "value_as_number": [10.0, 20.0, 30.0, 40.0],
                        "flag": [1, 0, 1, 1],
                    }
                )
            ),
            "cohort_b": SimpleNamespace(
                df=pd.DataFrame(
                    {
                        "patient_id": [1, 2],
                        "value_as_number": [100.0, 200.0],
                        "flag": [0, 0],
                    }
                )
            ),
        }

    def tearDown(self):
        tre.Spiredf = self.original_spiredf
        tre.TableDefinition.instances = self.original_instances

    def test_get_returns_registered_instance(self):
        rows = pd.DataFrame(columns=["var_name", "filter", "statistic"])
        cols = pd.DataFrame(columns=["cohort_a", "cohort_b"])

        table = tre.TableDefinition("demo", rows, cols)
        tre.TableDefinition.instances["demo"] = table

        self.assertIs(tre.TableDefinition.get("demo"), table)

    def test_str_contains_name_rows_and_columns(self):
        rows = pd.DataFrame(
            [
                {
                    "var_name": "patients",
                    "filter": "flag == 1",
                    "statistic": "count_rows",
                }
            ]
        )
        cols = pd.DataFrame(columns=["cohort_a", "cohort_b"])

        table = tre.TableDefinition("demo", rows, cols)
        text = str(table)

        self.assertIn("demo", text)
        self.assertIn("cohort_a", text)
        self.assertIn("cohort_b", text)
        self.assertIn("patients", text)
        self.assertIn("count_rows", text)

    def test_compute_cell_tab_supported_statistics(self):
        table = tre.TableDefinition(
            "demo",
            pd.DataFrame(columns=["var_name", "filter", "statistic"]),
            pd.DataFrame(columns=["cohort_a"]),
        )
        df = FakeSpiredf.get("cohort_a").df

        cases = {
            "count_unique_pts": 3,
            "count_rows": 4,
            "micro_mean": 25.0,
            "macro_mean": (15.0 + 30.0 + 40.0) / 3.0,
        }

        for stat, expected in cases.items():
            with self.subTest(stat=stat):
                row = pd.Series({"statistic": stat})
                value = table.compute_cell_tab("cohort_a", row, df)

                if isinstance(expected, float):
                    self.assertAlmostEqual(value, expected)
                else:
                    self.assertEqual(value, expected)

    def test_compute_cell_tab_unknown_statistic_raises(self):
        table = tre.TableDefinition(
            "demo",
            pd.DataFrame(columns=["var_name", "filter", "statistic"]),
            pd.DataFrame(columns=["cohort_a"]),
        )
        df = FakeSpiredf.get("cohort_a").df
        row = pd.Series({"statistic": "not_supported"})

        with self.assertRaises(ValueError):
            table.compute_cell_tab("cohort_a", row, df)

    def test_compute_tab_applies_filter_and_handles_errors(self):
        rows = pd.DataFrame(
            [
                {
                    "var_name": "filtered_rows",
                    "filter": "flag == 1",
                    "statistic": "count_rows",
                },
                {
                    "var_name": "unique_patients",
                    "filter": None,
                    "statistic": "count_unique_pts",
                },
                {
                    "var_name": "bad_stat",
                    "filter": None,
                    "statistic": "unknown_stat",
                },
            ]
        )
        cols = pd.DataFrame(columns=["cohort_a", "cohort_b"])

        table = tre.TableDefinition("demo", rows, cols)
        result = table.compute_tab()

        self.assertEqual(
            list(result.columns),
            ["var_name", "filter", "statistic", "cohort_a", "cohort_b"],
        )

        self.assertEqual(result.loc[0, "cohort_a"], 3)
        self.assertEqual(result.loc[0, "cohort_b"], 0)

        self.assertEqual(result.loc[1, "cohort_a"], 3)
        self.assertEqual(result.loc[1, "cohort_b"], 2)

        self.assertEqual(result.loc[2, "cohort_a"], "E")
        self.assertEqual(result.loc[2, "cohort_b"], "E")


if __name__ == "__main__":
    unittest.main()
# %%
