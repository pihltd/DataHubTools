#Add file IDs to a file manifest

import argparse
import pandas as pd
import uuid

def main(args):
    
    fp = 'dg.4DFC/'
    
    df = pd.read_csv(args.filemanifest, sep="\t")
    for index, row in df.iterrows():
        df.loc[index, 'file_id'] = fp+str(uuid.uuid4())
        #df.at[index, 'file_id'] = fp+str(uuid.uuid4())
        
    df.to_csv(args.filemanifest+".id.csv", sep="\t", index=False)
    



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--filemanifest", required=True,  help="DH File Manifest")
    parser.add_argument("-v", "--verbose", help="Verbose Output")

    args = parser.parse_args()

    main(args)