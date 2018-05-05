import pandas
import logger
from data_transformation_util import DataTransformationUtil


class DataCheckUtil:
    @staticmethod
    def check_duplicates(dataframe, check_column=False, check_row=False):
        # checks if dataframe contains duplicate columns
        if check_column is True:
            dataframe_transpose = dataframe.T
            dataframe_row_dedup = dataframe_transpose[~dataframe_transpose.index.duplicated()]
            row_count_diff = len(dataframe_transpose.index) - len(dataframe_row_dedup.index)
            if row_count_diff > 0:
                return True
            return False

        # checks if dataframe contains duplicate rows
        if check_row is True:
            dataframe_row_dedup = dataframe[~dataframe.index.duplicated()]
            row_count_diff = len(dataframe.index) - len(dataframe_row_dedup.index)
            if row_count_diff > 0:
                return True
            return False

    @staticmethod
    def check_duplicate_column_name(dataframe):
        """
        Checks duplicate column names and rejects it if it exists

        Args:
            dataframe: input dataframe to be checked

        Returns:
            user_spreadsheet_df_genename_dedup.T: a DataFrame in original format
            ret_msg: error message
        """

        dataframe_transpose = dataframe.T
        dataframe_row_dedup = dataframe_transpose[~dataframe_transpose.index.duplicated()]
        if dataframe_row_dedup.empty:
            logger.logging.append("ERROR: User spreadsheet becomes empty after remove column duplicates.")
            return None

        row_count_diff = len(dataframe_transpose.index) - len(dataframe_row_dedup.index)

        if row_count_diff > 0:
            logger.logging.append(
                "WARNING: Removed {} duplicate column(s) from user spreadsheet.".format(row_count_diff))
            return dataframe_row_dedup.T

        if row_count_diff == 0:
            logger.logging.append("INFO: No duplicate column name detected in this data set.")
            return dataframe_row_dedup.T

        if row_count_diff < 0:
            logger.logging.append("ERROR: An unexpected error occurred during checking duplicate column name.")
            return None

    @staticmethod
    def check_duplicate_row_name(dataframe):
        """
        Checks duplication on gene name and rejects it if it exists.

        Args:
            dataframe: input DataFrame

        Returns:
            dataframe_genename_dedup: a DataFrame in original format
            ret_msg: error message
        """
        dataframe_genename_dedup = dataframe[~dataframe.index.duplicated()]
        if dataframe_genename_dedup.empty:
            logger.logging.append("ERROR: User spreadsheet becomes empty after remove column duplicates.")
            return None

        row_count_diff = len(dataframe.index) - len(dataframe_genename_dedup.index)
        if row_count_diff > 0:
            logger.logging.append("WARNING: Removed {} duplicate row(s) from user spreadsheet.".format(row_count_diff))
            return dataframe_genename_dedup

        if row_count_diff == 0:
            logger.logging.append("INFO: No duplicate row name detected in this data set.")
            return dataframe_genename_dedup

        if row_count_diff < 0:
            logger.logging.append("ERROR: An unexpected error occurred during checking duplicate row name.")
            return None

    @staticmethod
    def check_intersection_for_phenotype_and_user_spreadsheet(dataframe_header, phenotype_df_pxs):
        '''
        Checks intersection between phenotype data and user spreadsheet on each drug

        Args:
            dataframe_header: the header of dataframe as a list
            phenotype_df_pxs: phenotype dataframe in phenotype x sample

        Returns:
            phenotype_df_pxs_trimmed: a trimmed phenotype dataframe

        '''
        # a list to store headers that has intersection between phenotype data and user spreadsheet
        valid_samples = []

        # loop through phenotype (phenotype x sample) to check header intersection between phenotype and spreadsheet
        for column in range(0, len(phenotype_df_pxs.columns)):
            # drops columns with NA value in phenotype dataframe
            phenotype_df_sxp = phenotype_df_pxs.ix[:, column].to_frame().dropna(axis=0)
            phenotype_index = list(phenotype_df_sxp.index.values)
            # finds common headers
            common_headers = set(phenotype_index) & set(dataframe_header)
            cur_column_name = phenotype_df_pxs.columns[column]
            if not common_headers:
                logger.logging.append(
                    "WARNING: Cannot find intersection on phenotype between user spreadsheet and "
                    "phenotype data on column: {}. Removing it now.".format(cur_column_name))
            elif len(common_headers) < 2:
                logger.logging.append(
                    "WARNING: Number of samples is too small to run further tests (Pearson, t-test) "
                    "on column: {}. Removing it now.".format(cur_column_name))
            else:
                valid_samples.append(phenotype_df_pxs.columns[column])

        if len(valid_samples) == 0:
            logger.logging.append("ERROR: Cannot find any valid column in phenotype data "
                                  "that has intersection with spreadsheet data.")
            return None

        # remove the columns that doesn't contain intersections in phenotype data
        phenotype_df_pxs_trimmed = phenotype_df_pxs[sorted(valid_samples)]

        return phenotype_df_pxs_trimmed

    @staticmethod
    def compare_order(list_a, list_b):
        """
        Checks if the input two lists are the same, including order.
        Args:
            list_a: list a
            list_b: list b
        Returns:
            True: list a and b are exactly the same
            False: list a and b are not same
        """
        if list_a == list_b:
            return True
        elif sorted(list_a) == sorted(list_b):
            return False
        else:
            return False

    @staticmethod
    def sanity_check_input_data(self, input_dataframe):
        """
        Checks the validity of user input spreadsheet data file, including duplication and nan

        Args:
            input_dataframe: user spreadsheet input file DataFrame, which is uploaded from frontend
            run_parameters: run_file parameter dictionary

        Returns:
            flag: Boolean value indicates the status of current check
            message: A message indicates the status of current check
        """
        logger.logging.append("INFO: Start to run sanity checks for input data.")

        # Case 1: removes NA rows in index
        input_dataframe_idx_na_rmd = DataTransformationUtil.remove_na_index(input_dataframe)
        if input_dataframe_idx_na_rmd is None:
            return None

        # Case 2: checks the duplication on column name and removes it if exists
        input_dataframe_col_dedup = DataCheckUtil.check_duplicate_column_name(input_dataframe_idx_na_rmd)
        if input_dataframe_col_dedup is None:
            return None

        # Case 3: checks the duplication on gene name and removes it if exists
        input_dataframe_genename_dedup = DataCheckUtil.check_duplicate_row_name(input_dataframe_col_dedup)
        if input_dataframe_genename_dedup is None:
            return None

        logger.logging.append("INFO: Finished running sanity check for input data.")

        return input_dataframe_genename_dedup

    @staticmethod
    def find_intersection(list_a, list_b):
        '''
        Find intersection between list_a, list_b
        Args:
            list_a: list a
            list_b: list b

        Returns:
            intersection: the intersection
        '''
        intersection = list(set(list_a) & set(list_b))
        if not intersection:
            logger.logging.append("ERROR: Cannot find intersection between spreadsheet and phenotype data.")
            return None
        logger.logging.append(
            "INFO: Found {} intersected gene(s) between phenotype and spreadsheet data.".format(len(intersection)))
        return intersection

    @staticmethod
    def run_pre_processing_phenotype_data(phenotype_df, user_spreadsheet_df_header):
        '''
        Pre-processing phenotype data. This includes checking for na index, duplicate column name and row name.
        Args:
            phenotype_df: input phenotype dataframe to be checked

        Returns:
            phenotype_df_genename_dedup: cleaned phenotype dataframe
        '''
        logger.logging.append("INFO: Start to pre-process phenotype data.")

        phenotype_df_genename_dedup = DataCheckUtil.sanity_check_input_data(phenotype_df)
        if phenotype_df_genename_dedup is None:
            return None

        # Case 4: checks the intersection on phenotype
        intersection = DataCheckUtil.find_intersection(phenotype_df_genename_dedup.index.values,
                                                       user_spreadsheet_df_header)
        if intersection is None:
            return None

        logger.logging.append("INFO: Finished running sanity check for phenotype data.")

        return phenotype_df_genename_dedup

    @staticmethod
    def sanity_check_input_data(dataframe):
        """
        Checks the validity of user input spreadsheet data file, including duplication and nan

        Args:
            input_dataframe: user spreadsheet input file DataFrame, which is uploaded from frontend
            run_parameters: run_file parameter dictionary

        Returns:
            flag: Boolean value indicates the status of current check
            message: A message indicates the status of current check
        """
        logger.logging.append("INFO: Start to run sanity checks for input data.")

        # Case 1: removes NA rows in index
        input_dataframe_idx_na_rmd = DataTransformationUtil.remove_na_index(dataframe)
        if input_dataframe_idx_na_rmd is None:
            return None

        # Case 2: checks the duplication on column name and removes it if exists
        input_dataframe_col_dedup = DataCheckUtil.check_duplicate_column_name(input_dataframe_idx_na_rmd)
        if input_dataframe_col_dedup is None:
            return None

        # Case 3: checks the duplication on gene name and removes it if exists
        input_dataframe_genename_dedup = DataCheckUtil.check_duplicate_row_name(input_dataframe_col_dedup)
        if input_dataframe_genename_dedup is None:
            return None

        logger.logging.append("INFO: Finished running sanity check for input data.")

        return input_dataframe_genename_dedup

    @staticmethod
    def compare_order(list_a, list_b):
        """
        Checks if the input two lists are the same, including order.

        Args:
            list_a: list a
            list_b: list b

        Returns:
            True: list a and b are exactly the same
            False: list a and b are not same

        """
        if list_a == list_b:
            return True
        elif sorted(list_a) == sorted(list_b):
            return False
        else:
            return False

    @staticmethod
    def check_user_spreadsheet_data(dataframe, check_na=False, dropna_colwise=False, check_real_number=False,
                                    check_positive_number=False):
        """
        Customized checks for input data (contains NA value, contains all real number, contains all positive number)
        Args:
            dataframe: input DataFrame to be checked
            check_na: check NA in DataFrame
            dropna_colwise: drop column which contains NA
            check_real_number: check only real number exists in DataFrame
            check_positive_number: check only positive number exists in DataFrame

        Returns:
            dataframe: cleaned DataFrame
        """
        # drop NA column wise in dataframe
        if dropna_colwise is True:
            # drops column which check NA in dataframe
            org_column_count = dataframe.shape[1]
            dataframe = dataframe.dropna(axis=1)
            diff_count = org_column_count - dataframe.shape[1]
            if diff_count > 0:
                logger.logging.append("INFO: Remove {} column(s) which contains NA.".format(diff_count))

            if dataframe.empty:
                logger.logging.append("ERROR: User spreadsheet is empty after removing NA column wise.")
                return None

        # checks if dataframe contains NA value
        if check_na is True:
            if dataframe.isnull().values.any():
                logger.logging.append("ERROR: This user spreadsheet contains NaN value.")
                return None

        # checks real number negative to positive infinite
        if check_real_number is True:
            if False in dataframe.applymap(lambda x: isinstance(x, (int, float))).values:
                logger.logging.append("ERROR: Found non-numeric value in user spreadsheet.")
                return None

        # checks if dataframe contains only non-negative number
        if check_positive_number is True:
            if False in dataframe.applymap(lambda x: x >= 0).values:
                logger.logging.append("ERROR: Found negative value in user spreadsheet.")
                return None

        return dataframe

    @staticmethod
    def check_phenotype_data(phenotype_df_pxs, correlation_measure):
        """
        Verifies data value for t-test and pearson separately.

        Args:
            phenotype_df_pxs: phenotype data
            correlation_measure: correlation measure: pearson or t-test

        Returns:
            phenotype_df_pxs: cleaned phenotype data

        """
        # defines the default values that can exist in phenotype data
        if correlation_measure == 't_test':
            list_values = pandas.unique(phenotype_df_pxs.values.ravel())
            if len(list_values) < 2:
                logger.logging.append(
                    "ERROR: t_test requests at least two categories in your phenotype dataset. "
                    "Please revise your phenotype data and reupload.")
                return None

            for column in phenotype_df_pxs:
                cur_col = phenotype_df_pxs[[column]].dropna(axis=0)

                if not cur_col.empty:
                    if cur_col[column].dtype == object:
                        cur_df_lowercase = cur_col.apply(lambda x: x.astype(str).str.lower())
                    else:
                        cur_df_lowercase = cur_col

                    count_values = cur_df_lowercase[column].value_counts()
                    if count_values[count_values < 2].size > 0:
                        logger.logging.append(
                            "ERROR: t_test requires at least two unique values per category in phenotype data.")
                        return None

        if correlation_measure == 'pearson':
            if False in phenotype_df_pxs.applymap(lambda x: isinstance(x, (int, float))):
                logger.logging.append(
                    "ERROR: Only numeric value is allowed in phenotype data when running pearson test. "
                    "Found non-numeric value in phenotype data.")
                return None

        return phenotype_df_pxs

    @staticmethod
    def check_intersection_for_phenotype_and_user_spreadsheet(dataframe_header, phenotype_df_pxs):
        '''
        Checks intersection between phenotype data and user spreadsheet on each drug

        Args:
            dataframe_header: the header of dataframe as a list
            phenotype_df_pxs: phenotype dataframe in phenotype x sample

        Returns:
            phenotype_df_pxs_trimmed: a trimmed phenotype dataframe

        '''
        # a list to store headers that has intersection between phenotype data and user spreadsheet
        valid_samples = []

        # loop through phenotype (phenotype x sample) to check header intersection between phenotype and spreadsheet
        for column in range(0, len(phenotype_df_pxs.columns)):
            # drops columns with NA value in phenotype dataframe
            phenotype_df_sxp = phenotype_df_pxs.ix[:, column].to_frame().dropna(axis=0)
            phenotype_index = list(phenotype_df_sxp.index.values)
            # finds common headers
            common_headers = set(phenotype_index) & set(dataframe_header)
            cur_column_name = phenotype_df_pxs.columns[column]
            if not common_headers:
                logger.logging.append(
                    "WARNING: Cannot find intersection on phenotype between user spreadsheet and "
                    "phenotype data on column: {}. Removing it now.".format(cur_column_name))
            elif len(common_headers) < 2:
                logger.logging.append(
                    "WARNING: Number of samples is too small to run further tests (Pearson, t-test) "
                    "on column: {}. Removing it now.".format(cur_column_name))
            else:
                valid_samples.append(phenotype_df_pxs.columns[column])

        if len(valid_samples) == 0:
            logger.logging.append("ERROR: Cannot find any valid column in phenotype data "
                                  "that has intersection with spreadsheet data.")
            return None

        # remove the columns that doesn't contain intersections in phenotype data
        phenotype_df_pxs_trimmed = phenotype_df_pxs[sorted(valid_samples)]

        return phenotype_df_pxs_trimmed

    @staticmethod
    def validate_inputs_for_gp_fp(user_spreadsheet_df, phenotype_df, correlation_measure):
        """
        Input data check for Gene_Prioritization_Pipeline/Feature_Prioritization_Pipeline.

        Args:
            run_parameters: input configuration table

        Returns:
            user_spreadsheet_df_dropna: cleaned user spreadsheet
            phenotype_df_pxs: phenotype data

        """
        # Checks na, real number in user spreadsheet
        user_spreadsheet_df_chk = DataCheckUtil.check_user_spreadsheet_data(user_spreadsheet_df, dropna_colwise=True,
                                                                            check_real_number=True)
        if user_spreadsheet_df_chk is None or user_spreadsheet_df_chk.empty:
            logger.logging.append("ERROR: After drop NA, user spreadsheet data becomes empty.")
            return None, None

        # Checks value of phenotype dataframe for t-test and pearson
        logger.logging.append("INFO: Start to run checks for phenotypic data.")
        phenotype_df_chk = DataCheckUtil.check_phenotype_data(phenotype_df, correlation_measure)
        if phenotype_df_chk is None:
            return None, None

        # Checks intersection between user_spreadsheet_df and phenotype data
        user_spreadsheet_df_header = list(user_spreadsheet_df_chk.columns.values)
        phenotype_df_trimmed = DataCheckUtil.check_intersection_for_phenotype_and_user_spreadsheet(
            user_spreadsheet_df_header,
            phenotype_df_chk)
        if phenotype_df_trimmed is None or phenotype_df_trimmed.empty:
            logger.logging.append("ERROR: After drop NA, phenotype data becomes empty.")
            return None, None

        logger.logging.append("INFO: Finished running checks for phenotypic data.")

        return user_spreadsheet_df_chk, phenotype_df_trimmed

