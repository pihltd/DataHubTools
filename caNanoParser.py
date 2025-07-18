import json
import pandas as pd
from os import walk
import os
import yaml



def recursiveParse(jsonobj, targetkey, counter):
    #print(f"Looking for {targetkey} on pass {str(counter)}")
    #print(f"jsonobj is a {type(jsonobj)}")
    targetvalue = None
    if targetvalue is not None:
        return targetvalue
    elif type(jsonobj) is dict: 
        #print(f"Key Set: {list(jsonobj.keys())}")
        for key in jsonobj:
            if targetvalue is not None:
                return targetvalue
            elif key == targetkey:
                #print("FOUND MATCH")
                targetvalue = jsonobj[key]
                return targetvalue
            else:
                targetvalue = recursiveParse(jsonobj[key], targetkey, counter+1)
    
    
def getJsonValue(jsonthign, keystring):
    keylist = keystring.split("|")
    targetkey = keylist[-1]
    targetvalue = recursiveParse(jsonthign, targetkey, 1)
    return targetvalue



finaljson = {
    'study': pd.DataFrame(columns=['study_name', 'study_description', 'study_external_url', 'study_data_types', 'role_or_affiliation', 'first_name', 'last_name']),
    'sample': pd.DataFrame(columns=['sample_id'])
}


jsonfiles = [r'C:\Users\pihltd\OneDrive - National Institutes of Health\FNLCR Projects\General Commons Cancer Data Services\caNanoLab\SampleJSON\caNanoLab_sample_data_1752256035098.json']
jsonpath = r'C:\Users\pihltd\OneDrive - National Institutes of Health\FNLCR Projects\General Commons Cancer Data Services\caNanoLab\SampleJSON'
outdir = r"C:\Users\pihltd\OneDrive - National Institutes of Health\FNLCR Projects\General Commons Cancer Data Services\caNanoLab\SampleJSON"
mappingfile = r"C:\Users\pihltd\Documents\github\DataHubTools\canano_gc_mapping.yml"
with open(mappingfile, "r") as f:
    mappings = yaml.load(f, Loader=yaml.FullLoader)
#print(mappings['mappings'].keys())

filenames = next(walk(jsonpath), (None, None,[]))[2]
for file in filenames:
    if '.json' in file:
        #print(os.path.join(jsonpath, file))
        fullfile = os.path.join(jsonpath, file)
        with open(fullfile,'r', encoding='utf-8') as f:
            workingjson = json.load(f)
        workingjson = workingjson[0]['sample']
        nodelist = list(finaljson.keys())
        #print(nodelist)
        for node in nodelist:
            temp_df = finaljson[node]
            storage = {}
            if node in mappings['mappings'].keys():
                #print(f"Starting to look for {node}")
                for prop, keystring in mappings['mappings'][node].items():
                    jsonvalue = getJsonValue(workingjson, keystring)
                    #print(f"Prop: {prop}\tReturned value: {jsonvalue}")
                    storage[prop] = jsonvalue
                temp_df.loc[len(temp_df)] = storage
            finaljson[node] = temp_df
            
for node, df in finaljson.items():
    filename = os.path.join(outdir, f"{node}_loadsheet.csv")
    df.to_csv(filename, sep="\t", index=False )
            
            