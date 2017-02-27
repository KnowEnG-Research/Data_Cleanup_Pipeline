import unittest
import pandas as pd
import data_cleanup_toolbox as data_cln
import os


class Testcheck_input_value_for_geneset_characterization(unittest.TestCase):
    def setUp(self):
        self.input_df = pd.DataFrame([[1, 0],
                                      [0, 0],
                                      [1, 1]],
                                     index=['ENSG00001027003', "ENSG00001027003", 'ENSG00008000303'],
                                     columns=['a', 'b'])
        self.input_nan_df = pd.DataFrame([[1, 0],
                                          [0, None],
                                          [1, 1]],
                                         index=['ENSG00001027003', "ENSG00001027003", 'ENSG00008000303'],
                                         columns=['a', 'b'])

        self.run_parameters_sc = {
            "spreadsheet_name_full_path": "../data/spreadsheets/example.tsv",
            "results_directory": "./",
            "source_hint": "",
            "taxonid": '9606',
            "pipeline_type": "geneset_characterization_pipeline"
        }

    def tearDown(self):
        del self.input_df
        del self.input_nan_df
        del self.run_parameters_sc

    def test_check_input_value_for_geneset_characterization_pass(self):
        ret_df, ret_msg = data_cln.check_input_value_for_geneset_characterization(self.input_df, self.run_parameters_sc)
        ret_flag = ret_df is not None
        self.assertEqual(True, ret_flag)

    def test_check_nan_input_value(self):
        ret_df, ret_msg = data_cln.check_input_value_for_geneset_characterization(self.input_nan_df, self.run_parameters_sc)
        ret_flag = ret_df is not None
        self.assertEqual(False, ret_flag)


if __name__ == '__main__':
    unittest.main()
