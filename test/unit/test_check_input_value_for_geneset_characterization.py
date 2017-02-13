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

        self.input_phenotype_df = pd.DataFrame(
            [[1.1, 2.2, 3.3]],
            index=['drug1'],
            columns=['a', 'b', 'c']
        )

        self.input_phenotype_df_bad = pd.DataFrame(
            [[1.1, 2.2, 3.3]],
            index=['drug1'],
            columns=['d', 'e', 'f']
        )

        self.run_parameters_sc = {
            "spreadsheet_name_full_path": "../data/spreadsheets/example.tsv",
            "phenotype_full_path": "../data/spreadsheets/phenotype.tsv",
            "results_directory": "./",
            "source_hint": "",
            "taxonid": '9606',
            "pipeline_type": "samples_clustering_pipeline"
        }

        self.pipeline_sc = "samples_clustering_pipeline"
        self.data_type = "user_spreadsheet"
        self.phenotype_output = "./phenotype_ETL.tsv"

    def tearDown(self):
        del self.input_df
        del self.input_phenotype_df
        del self.input_nan_df
        del self.run_parameters_sc
        del self.pipeline_sc
        del self.data_type
        del self.phenotype_output

    def test_check_input_value_for_geneset_characterization_pass(self):
        ret_df, ret_msg = data_cln.check_input_value_for_geneset_characterization(self.input_df, self.input_phenotype_df,
                                                             self.run_parameters_sc)
        ret_flag = ret_df is not None
        self.assertEqual(True, ret_flag)
        os.remove(self.phenotype_output)

    def test_check_nan_input_value(self):
        ret_df, ret_msg = data_cln.check_input_value_for_geneset_characterization(self.input_nan_df, self.input_phenotype_df,
                                                             self.run_parameters_sc)
        ret_flag = ret_df is not None
        self.assertEqual(False, ret_flag)


if __name__ == '__main__':
    unittest.main()
