import xml.etree.ElementTree as et
import pandas as pd

dbgapinfo_df = pd.DataFrame(columns=['submitted_subject_id', 'gap_subject_id'])
missingfixed_df = pd.DataFrame(columns=['participant_id', 'dbgap_subject_id', 'consent_code', 'consent_abbreviation', 'phs_accession'])

xmlfiles = [r'C:\Users\pihltd\Documents\ConsentCodes\xml\phs0000720_biosample_result.xml', r'C:\Users\pihltd\Documents\ConsentCodes\xml\phs001524_biosample_result.xml']
#xmlfiles = [r'C:\Users\pihltd\Documents\ConsentCodes\xml\phs0000720_biosample_result.xml']
missingfile = r'C:\Users\pihltd\Documents\ConsentCodes\ConsentMissing.csv'
outputfile = r'C:\Users\pihltd\Documents\ConsentCodes\ConsentMissing_fixed.csv'

missing_df = pd.read_csv(missingfile, sep="\t")


for xmlfile in xmlfiles:
    tree = et.parse(xmlfile)
    root = tree.getroot()
    for attributes in root.findall("./BioSample/Attributes"):
        for attribute in attributes.findall("./Attribute"):
            if attribute.attrib['attribute_name'] == 'submitted subject id':
                sub_id = attribute.text
            elif attribute.attrib['attribute_name'] == 'gap_subject_id':
                gap_id = attribute.text
        dbgapinfo_df.loc[len(dbgapinfo_df)] = {'submitted_subject_id':sub_id, 'gap_subject_id': gap_id}
        
for index, row in missing_df.iterrows():
    id = row['participant_id']
    if id in dbgapinfo_df['submitted_subject_id'].unique():
        dbgapid = dbgapinfo_df.query('submitted_subject_id == @id').iloc[0,1]
    else:
        dbgapid = 'Not Found'
    #print(f"SearchID: {id}\nReturned Info: {dbgapid}")
    missingfixed_df.loc[len(missingfixed_df)] = {'participant_id': id, 'dbgap_subject_id': dbgapid , 'consent_code': row['consent_code'], 'consent_abbreviation': row['consent_abbreviation'], 'phs_accession': row['phs_accession']}

missingfixed_df.to_csv(outputfile, sep="\t")

    