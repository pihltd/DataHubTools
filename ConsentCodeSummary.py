import pandas as pd
import numpy as np
import os

directory = r"C:\Users\pihltd\Documents\ConsentCodes"

filelist = os.listdir(directory)
summary_df = pd.DataFrame(columns=['ConsentAbbreviation', 'Count', 'PHS'])
missing_df = pd.DataFrame(columns=['participant_id', 'dbgap_subject_id', 'consent_code', 'consent_abbreviation', 'phs_accession'])

for file in filelist:
    if 'phs' in file:
        fullfile = directory+'\\'+file
        phs = file.split("_")[0]
        temp_df = pd.read_csv(fullfile, sep="\t")
        # Convert NaN to None
        temp_df = temp_df.replace([np.nan], ['None'], regex=False)
        stuff = temp_df.value_counts('consent_abbreviation', dropna=False).to_dict()
        for code, count in stuff.items():
            summary_df.loc[len(summary_df)] = {'ConsentAbbreviation': code, 'Count':count, 'PHS':phs}
        #Now add all missing to a missing dataframe
        for index, row in temp_df.iterrows():
            #print(row['consent_abbreviation'])
            if row['consent_abbreviation'] == 'None':
                missing_df.loc[len(missing_df)] = row
outfile = directory+'\\'+'ConsentSummary.csv'
summary_df.to_csv(outfile, sep="\t", index=False)
missingfile = directory+'\\'+'ConsentMissing.csv'
missing_df.to_csv(missingfile, sep="\t", index=False)
    