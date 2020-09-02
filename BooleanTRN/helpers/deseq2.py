#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# Functions related to DESeq2 data analysis

import pandas as pd
from BooleanTRN.constants import BASE_NODES


def _combine_files(results: str, id_to_name: str) -> pd.DataFrame:
    if id_to_name is None:
        data = pd.read_csv(results)
        data = data.sort_values(by="padj").drop_duplicates(
            subset='gene_id').reset_index(drop=True)
        data['Gene name'] = data['gene_id']
        return data
    names = pd.read_csv(id_to_name, sep="\t")
    data = pd.read_csv(results)
    data = data.sort_values(by="padj").drop_duplicates(subset='gene_id')
    data = data.set_index('gene_id')
    names = names.drop_duplicates(subset='Gene stable ID')
    names = names.set_index("Gene stable ID")[['Gene name']]
    data = pd.concat([data, names], axis=1, join='outer')
    data = data.rename_axis("gene_id").reset_index()
    return data


def check_expression_changes(
        results: str,
        genes: list,
        id_to_name: str = None):
    """
    :param genes: Names of the genes
    :param results: DESeq2 result file in csv format
    :param id_to_name: if IDs are in ENSDARG*** format, you can provide file
     with ID to name mapping with header as "Gene stable ID" (id) and
     "Gene name" (gene name). You can get this file from BioMart. This will
     be tab separated file.
    :return:
    """
    data = _combine_files(results, id_to_name)
    data = data[data['Gene name'].isin(genes)][['Gene name',
                                                'log2FoldChange', 'padj']]
    print(data)


def run():
    temp_result_file = "data/star.result_lfc.csv"
    temp_id_file = "data/id_to_name_21_01_2020.tsv"
    genes = BASE_NODES
    check_expression_changes(temp_result_file, genes, temp_id_file)
