import json
import pandas as pd
import bento_mdf

def buildLoadsheets(mdf):
    loadsheets = {}
    nodenames = mdf.model.nodes.keys()
    for node in nodenames:
        props = mdf.model.nodes[node].props
        #print(list(props.keys()))
        loadsheets[node] = list(props.keys())
    return loadsheets

def buildLoadsheetsDataFrame(loadsheets):
    loadsheets_df = {}
    for key, value in loadsheets.items():
        temp_df = pd.DataFrame(columns=value)
        loadsheets_df[key] = temp_df
    return loadsheets_df
        


jsonfiles = [r'C:\Users\pihltd\OneDrive - National Institutes of Health\FNLCR Projects\General Commons Cancer Data Services\caNanoLab\SampleJSON\caNanoLab_sample_data_1752256035098.json']
outfile = r'C:\Users\pihltd\OneDrive - National Institutes of Health\FNLCR Projects\General Commons Cancer Data Services\caNanoLab\SampleJSON\nodeprops.csv'
#gdload_df = pd.DataFrame(columns=['sample_id', 'sample_type', 'sample_description', 'sample_type_category', 'sample_tumor_status'])
mdffiles = ['https://raw.githubusercontent.com/CBIIT/cds-model/refs/heads/main/model-desc/cds-model.yml',"https://raw.githubusercontent.com/CBIIT/cds-model/refs/heads/main/model-desc/cds-model-props.yml"]

#mdf = bento_mdf.mdf.MDF(*mdffiles)
#loadsheets = buildLoadsheets(mdf)
#print(loadsheets)

#loadsheets_df = buildLoadsheetsDataFrame(loadsheets)
#print(loadsheets_df)



for jfile in jsonfiles:
    with open(jfile, "r") as f:
        jsondata = json.load(f)
        jsondata = jsondata[0]
        
keyset = {}
#Just get rid of the sample for now, it's just annoying.
jsondata = jsondata['sample']
nodelist = list(jsondata.keys())
#print(nodelist)
out_df = pd.DataFrame(columns=['Node', 'Property', "Secondary Property", "Type"])
for node in nodelist:
    # The characterization section is a list, needs special handling
    if node != 'characterization':
        #print(f"entry node: {node}")
        list_1 = list(jsondata[node].keys())
        for listitem in list_1:
            #print(f"Node:\t{node}\tProperty:\t{listitem}\tType:\t{type(jsondata[node][listitem])}")
            addthis = {'Node':node, 'Property':listitem, 'Type': type(jsondata[node][listitem])}
            out_df.loc[len(out_df)] = addthis
            if type(jsondata[node][listitem]) is dict:
                list_2 = list(jsondata[node][listitem].keys())
                for listitem2 in list_2:
                    #print(f"Node:\t{node}\tProperty:\t{listitem}\tSecondaryProp:\t{listitem2}\tType:\t{type(jsondata[node][listitem][listitem2])}")
                    out_df.loc[len(out_df)] = {'Node':node, 'Property':listitem, 'Secondary Property':listitem2, 'Type': type(jsondata[node][listitem][listitem2])}

out_df.to_csv(outfile, sep="\t", index=False)
