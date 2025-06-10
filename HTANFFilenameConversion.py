import pandas as pd

#htanfile=r'C:\Users\pihltd\OneDrive - National Institutes of Health\FNLCR Projects\DataHub-DCC\UserIssues\HTAN\example_of_HTAN_distinct_files_with_identical_names.csv'
#outfile = r'C:\Users\pihltd\OneDrive - National Institutes of Health\FNLCR Projects\DataHub-DCC\UserIssues\HTAN\example_of_HTAN_distinct_files_with_identical_names_DHAdjusted.csv'

htanfile = r'C:\Users\pihltd\OneDrive - National Institutes of Health\FNLCR Projects\DataHub-DCC\UserIssues\HTAN\HTAN-MSK-File-Submission_file_202505121337.tsv'
outfile = r'C:\Users\pihltd\OneDrive - National Institutes of Health\FNLCR Projects\DataHub-DCC\UserIssues\HTAN\HTAN-MSK-File-Submission_file_202505121337_DHAdjusted.tsv'

htan_df = pd.read_csv(htanfile, sep="\t")

#print(htan_df.head())

htan_df['s3_filename'] = pd.Series(dtype=str)
htan_df['display_name'] = pd.Series(dtype=str)

for index, row in htan_df.iterrows():
    #fullfilename = row['Filename']
    #print(row)
    fullfilename = row['file_name']
    newfilename = fullfilename.replace(' ','_') #replace any spaces with underscores
    newfilename = newfilename.replace('/', '_') #replace slash with underscores
    #htan_df.loc[index, 's3_filename'] = fullfilename.replace('/','_')
    htan_df.loc[index, 's3_filename'] = newfilename
    htan_df.loc[index,'display_name'] = fullfilename.split('/')[-1]

#print(htan_df.head())
htan_df.to_csv(outfile, sep="\t", index=False)