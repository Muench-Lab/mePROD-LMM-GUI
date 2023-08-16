import warnings
import DynaTMT_SB as DynaTMT
import pbLMM_SB as statisticsGetter
import requests
import pandas as pd
warnings.filterwarnings("ignore")

class mePROD:
    def __init__(self, location):
        self.reports = open(f'{location}/reports.txt','w+')
        self.status = ''

    def engine(self, psms, conditions, pairs, normalization_type, statistics_type):
        channels = [col for col in psms.columns if 'Abundance:' in col]

        if channels == []:
            channels = [col for col in psms.columns if 'Abundance' in col]

        s = 0
        for condition in conditions: # to remove abundances to skip (empty channels)
            if condition == 'skip':
                psms.drop(channels[s], axis=1, inplace=True)
            s+=1

        conditions = [x for x in conditions if not str(x).lower().__contains__('skip')] # to remove 'skip' from the conditions

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

        process = DynaTMT.PD_input(psms)
        # process.IT_adjustment()
        # process.total_intensity_normalisation()
        # process.filter_peptides() # earlier filter peptides after total intensity normalisation
        process.IT_adjustment()
        process.filter_peptides() # filter peptides before total intensity normalisation 19062023

        if normalization_type == 'total':
            process.total_intensity_normalisation()
        elif normalization_type == 'TMM':
            process.TMM()
        elif normalization_type == 'median':
            process.Median_normalisation()

        self.reports.write('The number of total peptides: {}\n'.format(len(psms.index)))

        heavy = process.extract_heavy()

        self.reports.write('The number of heavy peptides: {}\n'.format(len(heavy.index)))

        self.status = 'heavy'
        self.mito_count(heavy)

        peptide_data = process.baseline_correction_peptide_return(heavy,threshold=5, i_baseline=baselineIndex, random=True)

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
        #print(pairs)

        hypo = statisticsGetter.HypothesisTesting()

        if statistics_type == 'LMM':
            result = hypo.peptide_based_lmm(peptide_data,conditions=conditions,pairs=pairs)
        elif statistics_type == 'ttest':
            result = hypo.ttest(peptide_data, conditions=conditions, pairs=pairs)

        result = result.rename(columns=columnDict)
        self.reports.write('The number of heavy proteins: {}\n'.format(len(result.index)))

        result['Accession'] = result.index
        result['Gene Symbol'] = ''

        self.status = 'protein'
        self.mito_count(result)

        self.reports.close()
        return result

    def GeneNameEngine(self, Data):

        database = pd.read_excel('./files/Uniprot_database_2021.xlsx')
        accessionDatabase = list(database['Accession'])
        geneNameDatabase = list(database['Gene Symbol'])

        try:
            accession = list(Data['Master Protein Accessions'])
        except:
            accession = list(Data['Accession'])
        j = 0

        for i in accession:
            if ';' in i:
                final = i.split(';')[0]
            elif ' ' in i:
                final = i.split(' ')[0]
            else:
                final = i

            if final in accessionDatabase:
                index = accessionDatabase.index(final)
                geneSymbol = geneNameDatabase[index]

            else:
                try:
                    url = f'https://www.ebi.ac.uk/proteins/api/proteins/{final}'
                    req = requests.get(url)
                    result = req.json()
                    geneSymbol = result['gene'][0]['name']['value']
                except:
                    geneSymbol = ''

            Data.loc[j, 'Gene Symbol'] = geneSymbol
            j += 1

        return Data

    def mito_human(self, Data):

        try:
            AccessionNum = list(Data['Master Protein Accessions'])
        except:
            AccessionNum = list(Data['Accession'])

        database = pd.read_excel('./files/database.xlsx')
        MitoSymbol = list(database['Human_Mitochondrial'])
        j = 0

        for i in AccessionNum:
            try:
                result = i[0:6]
            except:
                j += 1
                continue

            if result in MitoSymbol:
                Data.loc[j, 'Accession new'] = result
                Data.loc[j, 'Mitochondrial Localization'] = 'YES'
            else:
                Data.loc[j, 'Accession new'] = result
                Data.loc[j, 'Mitochondrial Localization'] = 'NO'

            j += 1

        return Data

    def mito_count(self, Data):
        try:
            AccessionNum = list(Data['Master Protein Accessions'].astype(str))
        except:
            AccessionNum = list(Data['Accession'].astype(str))

        database = pd.read_excel('./files/database.xlsx')
        MitoSymbol_List = list(database['Human_Mitochondrial'].astype(str))
        MitoSymbol_List = sorted(MitoSymbol_List)
        AccessionNum = sorted(AccessionNum)
        j = 0
        k = 1
        for i in AccessionNum:
            try:
                result = i[0:6]
                if result in MitoSymbol_List:
                    k += 1
            except:
                j += 1
                continue

        if self.status == 'heavy':
            self.reports.write('The number of mitochondrial heavy peptides: {}\n'.format(k))
        if self.status == 'protein':
            self.reports.write('The number of mitochondrial heavy proteins: {}\n'.format(k))