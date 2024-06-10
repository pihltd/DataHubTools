#Demo on using a local datasource to validate a submission against a current set of CDE PVs
import pandas as pd
import requests
import json
import argparse
import pprint

def getCRDCCDEs():
    url = "https://cadsrapi.cancer.gov/rad/NCIAPI/1.0/api/DataElement/getCRDCList"
    headers = {"accept" : "application/json"}
    results = requests.get(url, headers=headers)
    return results.json()

def buildCDEDB(crdcjson):
    enum_columns = ["CRDC_Name", "Public_ID", "Version", "VM_Long_Name", "VM_Public_ID", "VM_Concept_Code"]
    truthy_df = pd.DataFrame(columns = enum_columns)

    crdcjson = crdcjson['CRDCDataElements']
    for element in crdcjson:
        if element['VD Type'] == 'Enumerated':
            for pv in element['permissibleValues']:
                truthy_df.loc[len(truthy_df.index)] = [element['CRDC Name'],element['CDE Public ID'], element["Version"],pv['VM Long Name'], pv['VM Public ID'], pv['Concept Code']]
        else:
            truthy_df.loc[len(truthy_df.index)] = [element['CRDC Name'],element['CDE Public ID'], element["Version"],None, None, None]
    return truthy_df

def validateThis(cde_id, truthy_df, term):
    cde_df = truthy_df[truthy_df['Public_ID'] == cde_id]
    #pprint.pprint(cde_df)
    if cde_df['VM_Long_Name'].eq(term).any():
        #print("Returning True")
        return True
    else:
        #print("Returning False")
        return False


def main(args):
    #First popluate a dataframe with the latest CRDC CDEs and PVs
    crdcjson = getCRDCCDEs()
    source_df = buildCDEDB(crdcjson)
    #pprint.pprint(source_df)

    searchterms = ["Normal Tissue Sample", "Wazooo"]
    cde_id = "14688604"
    for searchterm in searchterms:
        if validateThis(cde_id, source_df, searchterm):
            print(searchterm+" Validated")
        else:
            print(searchterm+" Error")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose",  help="Enable verbose messages")

    args = parser.parse_args()

    main(args)