"""
@author: The KnowEnG dev team
"""
from enum import Enum
import pandas as pd
import numpy as np
import knpackage.toolbox as kn


def uniform_phenotype_data(phenotype_df):
    """This is the preprocessing step to expand phenotype
    Parameters:
        phenotype_df: phenotype dataframe.
        threshold: threshold to determine which phenotype to remove.
    Returns:
        output_dict: dictionary with keys to be categories of phenotype data and values
        to be a list of related dataframes.
    """

    output_list = []

    for column in phenotype_df:
        cur_df = phenotype_df[[column]].dropna(axis=0)

        if not cur_df.empty:
            if cur_df[column].dtype == object:
                cur_df_lowercase = cur_df.apply(lambda x: x.astype(str).str.lower())
            else:
                cur_df_lowercase = cur_df

            output_list.append(cur_df_lowercase)

    return output_list


def phenotype_expander(run_parameters):
    """ Run phenotype expander on the whole dataframe of phenotype data.
    Save the results to tsv file.
    """
    phenotype_df = kn.get_spreadsheet_df(run_parameters['phenotype_name_full_path'])
    output_list = uniform_phenotype_data(phenotype_df)
    result_df = pd.DataFrame(index=phenotype_df.index)

    for item in output_list:
        col_df = phenotype_df.loc[:, item.columns[0]].dropna()
        uniq_array = np.unique(col_df.values)
        col_names = [item.columns[0] + '_' + str(i) for i in uniq_array]
        cur_df = pd.DataFrame(columns=col_names, index=col_df.index)
        cur_append_df = pd.DataFrame(columns=col_names, index=phenotype_df.index)
        print(uniq_array)
        for i, val in enumerate(uniq_array):
            print("i = {}, val = {}".format(i, val))
            cur_df.loc[col_df == val, col_names[i]] = 1
            cur_df.loc[col_df != val, col_names[i]] = 0
        cur_append_df.loc[cur_df.index, :] = cur_df
        result_df = pd.concat([result_df, cur_append_df], axis=1)

    result_df.index.name = "sample_id"

    return result_df

