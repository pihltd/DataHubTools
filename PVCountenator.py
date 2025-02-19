# Reads in an MDF model and creates a report of which CDEs have PVs and which don't.
from crdclib import crdclib
import bento_mdf
import pandas as pd

def getPermValues(cdeid, cdeversion):
    # Redo this so what's returned is a list of dictionary.  permissible_value:[{concept_code:source}]
    cdejson = crdclib.getCDERecord(cdeid, cdeversion)
    pvlist = []
    for pventry in cdejson['DataElement']['ValueDomain']['PermissibleValues']:
        #Within each pventry, there's a list at pventry['Concepts], and conceptCode has the NCIt code
        temp = []
        #print(f"ID: {cdeid}\tVersion: {cdeversion}")
        for concept in pventry['ValueMeaning']['Concepts']:
            conceptcode = concept['conceptCode']
            conceptsource = concept['evsSource']
            temp.append({conceptcode:conceptsource})
            #pvvalue = pventry['value']
        pvlist.append({pventry['value']:temp})
        #pvlist.append(pventry['value'])
    return pvlist

mdffiles = ['https://raw.githubusercontent.com/CBIIT/cds-model/refs/heads/main/model-desc/cds-model.yml', 'https://raw.githubusercontent.com/CBIIT/cds-model/refs/heads/main/model-desc/cds-model-props.yml']

mdf = bento_mdf.mdf.MDF(*mdffiles)

props = mdf.model.props

nopv = []
haspv = []

df = pd.DataFrame(columns=['Node', 'Property', 'PVs'])

# Enums are going to be found in a properties Term section
for prop in props:
    if mdf.model.props[prop].concept is not None:
        workingterms = mdf.model.props[prop].concept.terms.values()
        for workingterm in workingterms:
            temp = workingterm.get_attr_dict()
            enums = getPermValues(temp['origin_id'], temp['origin_version'])
            if len(enums) > 1:
                #haspv.append(prop)
                df.loc[len(df)] = {'Node':prop[0], 'Property': prop[1], 'PVs':'Yes'}
            else:
                #nopv.append(prop)
                df.loc[len(df)] = {'Node':prop[0], 'Property': prop[1], 'PVs':'No'}
            
    else:
        # If a property doesn't have a concept, by defintion, it doesn't have a PV set
        #nopv.append(prop)
        df.loc[len(df)] = {'Node':prop[0], 'Property': prop[1], 'PVs':'No'}
        
reportfile = r"C:\Users\pihltd\Documents\CDS_PV_Report.csv"
df.to_csv(reportfile, sep="\t", index=False) 