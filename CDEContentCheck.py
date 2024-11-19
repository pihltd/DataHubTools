# A summary report of how many properties in a node have CDEs
#import bento_mdf
#from bento_mdf.mdf import MDF
from crdclib import crdclib as cd
import argparse
import pandas as pd

def main(args):
    #mdf = MDF(args.modelfile, args.propfile, handle=args.handle)
    columns = ["Property", "Node", "CDE ID", "Description"]
    cde_df = pd.DataFrame(columns=columns)
    modeljson = cd.readYAML(args.modelfile)
    propjson = cd.readYAML(args.propfile)
    propjson = propjson['PropDefinitions']
    for node, info in modeljson['Nodes'].items():
        proplist = info['Props']
        for prop in proplist:
            cde_id = None
            desc = None
            if 'Term' in propjson[prop]:
                termlist = propjson[prop]['Term']
                for term in termlist:
                    cde_id = term['Code']
                    desc = term['Value']
                    cde_df.loc[len(cde_df.index)] = [prop, node, cde_id, desc]
            else:
                cde_df.loc[len(cde_df.index)] = [prop, node, cde_id, desc]
    notnull_df = cde_df[cde_df['CDE ID'].notnull()]
    isnull_df = cde_df[cde_df['CDE ID'].isnull()]
    notnull_df.to_csv(r"C:\Users\pihltd\Documents\VMShare\notnull.tsv", "\t")
    isnull_df.to_csv(r"C:\Users\pihltd\Documents\VMShare\isnull.tsv", "\t")
            
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--propfile", required=True, help="MDF Property File")
    parser.add_argument("-m", "--modelfile", required=True, help="MDF Model file")
    parser.add_argument("-d", "--handle", required=True, help="Model handle")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    main(args)