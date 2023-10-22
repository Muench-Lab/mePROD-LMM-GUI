import warnings
import DynaTMT_SB as DynaTMT
import PBLMM as statisticsGetter
import requests
import pandas as pd
warnings.filterwarnings("ignore")

class mePROD:
    def __init__(self, location, randomReportName):
        self.mito_database = pd.read_excel('./files/database.xlsx')
        self.geneNameDatabase = pd.read_excel('./files/Uniprot_database_2021.xlsx')
        self.reports = open(f'{location}/{randomReportName}.txt','w+')
        self.status = ''

    def engine(self, psms, conditions, pairs, normalization_type, statistics_type):
        channels = [col for col in psms.columns if 'Abundance:' in col]

        if channels == []:
            channels = [col for col in psms.columns if 'Abundance' in col]

        # to remove abundances to skip (empty channels) or boosters
        skip_terms = ['skip', 'boost', 'booster', 'mitobooster', 'wholecellbooster']
        s = 0
        for condition in conditions:
            if condition.lower() in skip_terms:
                psms.drop(channels[s], axis=1, inplace=True)
            s += 1

        conditions = [x for x in conditions if not any(term in str(x).lower() for term in skip_terms)]

        # we need to determine the baseline index from the conditions.
        # baselineIndex = conditions.index('baseline')

        # Convert the value and list elements to lowercase for case-insensitive search
        lower_conditions = [item.lower() for item in conditions]

        if 'light' in lower_conditions:
            baselineIndex = lower_conditions.index('light')
        elif "baseline" in lower_conditions:
            baselineIndex = lower_conditions.index("baseline")
        elif "base" in lower_conditions:
            baselineIndex = lower_conditions.index("base")
        elif "noise" in lower_conditions:
            baselineIndex = lower_conditions.index("noise")
        else:
            return 0

        # initialize the class with input data

        process = DynaTMT.PD_input()

        filtered_peptides = process.filter_peptides(
            psms)  # filter peptides before total intensity normalisation 19062023

        ITadjusted_peptides = process.IT_adjustment(filtered_peptides)

        self.reports.write('The number of total peptides: {}\n'.format(len(ITadjusted_peptides.index)))

        # process.total_intensity_normalisation()
        # process.filter_peptides() # earlier filter peptides after total intensity normalisation

        # the reason for filter peptieds before normalization is that we normalize what we are going to use

        normFinal = ''
        if normalization_type == 'total':
            normFinal = process.total_intensity_normalisation(ITadjusted_peptides)
        elif normalization_type == 'TMM':
            normFinal = process.TMM(ITadjusted_peptides)
        elif normalization_type == 'median':
            normFinal = process.Median_normalisation(ITadjusted_peptides)

        heavy = process.extract_heavy(normFinal)

        self.reports.write('The number of heavy peptides: {}\n'.format(len(heavy.index)))

        self.status = 'heavy'
        self.mito_count(heavy)

        peptide_data = process.baseline_correction(heavy, threshold=5, i_baseline=baselineIndex, random=True)

        #conditions=['Light','0DMSO','0DMSO','0DMSO','Rotenone','Rotenone','Rotenone','Antimycin','Antimycin','Antimycin','Boost']
        #pairs=[['0DMSO','Rotenone'], ['0DMSO','Antimycin']]

        conditions = [i.strip() for i in conditions]
        conditions = [i.lstrip() for i in conditions]

        channels = [col for col in peptide_data.columns if 'Abundance:' in col]
        if channels == []:
            channels = [col for col in peptide_data.columns if 'Abundance' in col]
        columnDict = {channels[i]: conditions[i] for i in range(len(channels))}

        #print(pairs)
        if pairs == [['']]:
            pairs = None

        if pairs != None:
            hypo = statisticsGetter.HypothesisTesting()
            if statistics_type == 'LMM':
                result = hypo.peptide_based_lmm(peptide_data,conditions=conditions,pairs=pairs)
            elif statistics_type == 'ttest':
                result = hypo.ttest(peptide_data, conditions=conditions, pairs=pairs)
        else:
            roll = statisticsGetter.Rollup()
            protein_data = roll.protein_rollup_sum(
                input_file=peptide_data, channels=channels)

            columnDict = {channels[i]: conditions[i] for i in range(len(channels))}
            protein_data = protein_data.rename(columns=columnDict)

            # Drop rows where the sum across the row (excluding 'index' column) is 0
            # this is especially important because of mePROD and basal level substraction makes 0 for entire row
            result = protein_data[protein_data.sum(axis=1) != 0]

        result = result.rename(columns=columnDict)
        self.reports.write('The number of heavy proteins: {}\n'.format(len(result.index)))

        result['Accession'] = result.index
        result['Gene Symbol'] = ''

        self.status = 'protein'
        self.mito_count(result)

        self.reports.close()

        # some numbers
        print(f"# of PSMs: {len(psms.index)}")
        print(f"# of filtered PSMs: {len(filtered_peptides.index)}")
        print(f"# of IT adjusted peptides: {len(ITadjusted_peptides.index)}")
        print(f"# of normalized peptides: {len(normFinal.index)}")
        print(f"# of heavy peptides: {len(heavy.index)}")
        print(f"# of baseline corrected peptides: {len(peptide_data.index)}")

        return result

    def GeneNameEngine(self, Data):
        # Convert the database to a dictionary for quicker lookups
        accession_to_gene = dict(zip(self.geneNameDatabase['Accession'], self.geneNameDatabase['Gene Symbol']))

        # Try to get the 'Master Protein Accessions' column, if not, get the 'Accession' column
        accession = Data.get('Master Protein Accessions', Data.get('Accession', pd.Series(dtype='object')))

        # Process the Accession numbers
        def process_accession(acc):
            if ';' in acc:
                return acc.split(';')[0]
            elif ' ' in acc:
                return acc.split(' ')[0]
            else:
                return acc

        # Fetch gene symbol
        def get_gene_symbol(final):
            if final in accession_to_gene:
                return accession_to_gene[final]
            else:
                try:
                    url = f'https://www.ebi.ac.uk/proteins/api/proteins/{final}'
                    req = requests.get(url)
                    result = req.json()
                    return result['gene'][0]['name']['value']
                except:
                    return ''

        processed_accessions = accession.apply(process_accession)
        Data['Gene Symbol'] = processed_accessions.apply(get_gene_symbol)

        return Data

    def mito_human(self, Data):
        # Try to get the 'Master Protein Accessions' column, if not, get the 'Accession' column
        AccessionNum = Data.get('Master Protein Accessions', Data.get('Accession', pd.Series(dtype='object')))

        # Read the database
        MitoSymbol = set(self.mito_database['Human_Mitochondrial'])

        # Process the Accession numbers
        def process_accession(acc):
            if ';' in acc:
                return acc.split(';')[0]
            elif '-' in acc:
                return acc.split('-')[0]
            else:
                return acc

        processed_accessions = AccessionNum.apply(process_accession)

        # Check if each processed accession number is in MitoSymbol
        Data['MitoCarta3.0'] = processed_accessions.apply(lambda x: '+' if x in MitoSymbol else '')

        return Data

    def mito_count(self, Data):
        # Try to get the 'Master Protein Accessions' column, if not, get the 'Accession' column
        AccessionNum = Data.get('Master Protein Accessions', Data.get('Accession', pd.Series(dtype='object'))).astype(
            str)

        MitoSymbol_Set = set(self.mito_database['Human_Mitochondrial'].astype(str))

        # Process the Accession numbers
        def process_accession(acc):
            if ';' in acc:
                return acc.split(';')[0]
            elif '-' in acc:
                return acc.split('-')[0]
            else:
                return acc

        processed_accessions = AccessionNum.apply(process_accession)
        count_mito = sum(1 for acc in processed_accessions if acc in MitoSymbol_Set)

        if self.status == 'heavy':
            self.reports.write('The number of mitochondrial heavy peptides: {}\n'.format(count_mito))
        if self.status == 'protein':
            self.reports.write('The number of mitochondrial heavy proteins: {}\n'.format(count_mito))

        return

    def significantAssig(self, Data):
        # Get all columns with 'p_value' and 'q_value' in their names
        pvalue_columns = [col for col in Data.columns if 'p_value' in col]
        qvalue_columns = [col for col in Data.columns if 'q_value' in col]

        # Iterate over the columns
        for i in range(0, len(pvalue_columns)):
            pcol = pvalue_columns[i]

            # Create a new column name for each p_value column (e.g. 'p_value CCCP_ISRIB/CCCP < 0.05')
            p_col_name = f'{pcol} < 0.05'

            # Assign '+' to rows where p_value is less than 0.05, else assign an empty string
            Data[p_col_name] = Data[pcol].apply(lambda x: '+' if x < 0.05 else '')

            if qvalue_columns != []:
                qcol = qvalue_columns[i]
                q_col_name = f'{qcol} < 0.05'
                Data[q_col_name] = Data[qcol].apply(lambda x: '+' if x < 0.05 else '')

        return Data