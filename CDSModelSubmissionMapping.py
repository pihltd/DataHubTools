#The purpose of this is to create a mapping file between the CDS submission sheet and the CDS Data Model
#This can use the config file from teh CDS2DataHubSubmissionSheets script

import pandas as pd
import yaml
import argparse
import pprint
import re

def readConfigs(yamlfile):
    with open(yamlfile) as f:
        configs = yaml.load(f, Loader=yaml.FullLoader)
    return configs

def exactMatch(dh, cds):
    #Go through each field in each DH template and see if there is an exact match in the CDS list
    #returns a dictionary.  Key is matched field, value is DH sheet field came from
    exact = {}
    for sheet, fields in dh.items():
        for field in fields:
            if field in cds:
                if sheet in exact:
                    exact[sheet].append(field)
                else:
                    exact[sheet] = [field]
    return exact    

def partialMatch(sheet, dhfield, cdsfields, dh2cds_partial):
    #Some of the DataHub fields have a . in the middle.  Split on that to get individual terms, but only use the back half
    dhfieldlist = dhfield.split('.')
    if len(dhfieldlist) > 1:
        dhitem = dhfieldlist[1]
    else:
        dhitem = dhfieldlist[0]
    #for dhitem in dhfieldlist:
    for cdsitem in cdsfields:
        #print(re.search(dhitem, cdsitem))
        if re.search(dhitem, cdsitem) is not None:
            if sheet in dh2cds_partial:
                #pprint.pprint(dh2cds_partial[sheet])
                dh2cds_partial[sheet].append({dhfield:cdsitem})
            else:
                dh2cds_partial[sheet] = [{dhfield:cdsitem}]
            #print(f"OriginalDHItem:  {dhfield} DHItem: {dhitem}   CDSItem:  {cdsitem}")
            #dh2cds_partial[dhfield] = cdsitem
                
def checkExact(sheet, field, reference):
    answer = True
    if sheet in reference:
        for entry in reference[sheet]:
                #print(f"Field: {field}  Entry: {entry}")
                if field in entry:
                    answer = False
    return answer

def unMapped(dhtemplate, exact, partial):
    unmapped = {}
    for sheet, fieldlist in dhtemplate.items():
        for field in fieldlist:
            inpart = checkExact(sheet, field, partial)
            inexact = checkExact(sheet, field, exact)
            #print(f"Checking {field} from {sheet} and Exact is {str(inexact)} and Partial is {str(inpart)}")
            if inexact and inpart:
                #print(f"Adding {field} to unmapped for {sheet}")
                if sheet in unmapped:
                    unmapped[sheet].append(field)
                else:
                    unmapped[sheet] = [field]
    return unmapped

def main(args):
    #Get the DataHub information
    configs = readConfigs(args.configfile)
    dhtemplates = configs['Templates']

    #Get the CDS Submission sheet fields
    Excel_df = pd.ExcelFile(configs['Ops']['input_file'])
    metadata_df = pd.read_excel(Excel_df, 'Metadata')
    cdsfields = metadata_df.columns.to_list()

    dh2cds_exact = exactMatch(dhtemplates, cdsfields)

    #For fields that aren't an exact match, look for partial matches
    dh2cds_partial = {}
    for sheet, fields in dhtemplates.items():
        for field in fields:
            if sheet in dh2cds_exact:
                if field not in dh2cds_exact[sheet]:
                 #type is a reserved word in the DH sheets used to describe what node the sheet is for.  Don't need to map it.
                    if field != 'type':
                     partialMatch(sheet, field, cdsfields, dh2cds_partial)
            else:
                if field != 'type':
                    partialMatch(sheet, field, cdsfields, dh2cds_partial)


    #Now create a list of all the fields in the sheets that did not map
    dh_unmapped = unMapped(dhtemplates, dh2cds_exact, dh2cds_partial)

    finalmapping = {}
    finalmapping['Exact'] = dh2cds_exact
    finalmapping['Partial'] = dh2cds_partial
    finalmapping['Unmapped'] = dh_unmapped

    with open('cdsmappin.yml', 'w') as f:
        yaml.dump(finalmapping, f)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")

    args = parser.parse_args()

    main(args)