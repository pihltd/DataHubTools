import xml.etree.ElementTree as et
import pandas as pd

dbgapinfo_df = pd.DataFrame(columns=['submitted_subject_id', 'gap_subject_id', 'submitted_sample_id', 'gap_sample_id', 'consent_code', 'consent_abbreviation'])
missingfixed_df = pd.DataFrame(columns=['participant_id', 'dbgap_subject_id', 'sample_id', 'dbgap_sample_id', 'consent_code', 'consent_abbreviation', 'phs_accession', 'comment'])

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
            elif attribute.attrib['attribute_name'] == 'submitted sample id':
                samp_id = attribute.text
            elif attribute.attrib['attribute_name'] == 'gap_sample_id':
                gap_samp_id = attribute.text
            elif attribute.attrib['attribute_name'] == 'gap_consent_code':
                concode = attribute.text
            elif attribute.attrib['attribute_name'] == 'gap_consent_short_name':
                conabb = attribute.text
        dbgapinfo_df.loc[len(dbgapinfo_df)] = {'submitted_subject_id':sub_id, 'gap_subject_id': gap_id, 'submitted_sample_id': samp_id, 'gap_sample_id': gap_samp_id, 'consent_code': concode, 'consent_abbreviation': conabb}
        
for index, row in missing_df.iterrows():
    dbgapid = 'Not Found'
    dbgapsampleid = 'Not Found'
    subsamp = 'Not Found'
    comment = 'No comment'
    conabbev = 'Missing'
    concode = 'Missing'
    id = row['participant_id']
    if id in dbgapinfo_df['submitted_subject_id'].unique():
        dbgaprow = dbgapinfo_df.loc[dbgapinfo_df['submitted_subject_id'] == id]
        dbgapid = dbgaprow.iloc[0]['gap_subject_id']
        subsamp = dbgaprow.iloc[0]['submitted_sample_id']
        dbgapsampleid = dbgaprow.iloc[0]['gap_sample_id']
        concode = dbgaprow.iloc[0]['consent_code']
        conabbev = dbgaprow.iloc[0]['consent_abbreviation']
        comment = 'Participant Match'
    elif id in dbgapinfo_df['submitted_sample_id'].unique():
        dbgaprow = dbgapinfo_df.loc[dbgapinfo_df['submitted_sample_id'] == id]
        dbgapid = dbgaprow.iloc[0]['gap_subject_id']
        subsamp = dbgaprow.iloc[0]['submitted_sample_id']
        dbgapsampleid = dbgaprow.iloc[0]['gap_sample_id']
        concode = dbgaprow.iloc[0]['consent_code']
        conabbev = dbgaprow.iloc[0]['consent_abbreviation']
        comment = 'Sample Match' 

    missingfixed_df.loc[len(missingfixed_df)] = {'participant_id': id, 'dbgap_subject_id': dbgapid, 'sample_id': subsamp, 'dbgap_sample_id': dbgapsampleid, 'consent_code': concode, 'consent_abbreviation': conabbev, 'phs_accession': row['phs_accession'], 'comment': comment}

missingfixed_df.to_csv(outputfile, sep="\t", index=False)

    