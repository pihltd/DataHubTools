#Gets data from ROR.org on organizations
import requests
import argparse
import zipfile
import os
from os import walk
import pandas as pd
import pprint

def getRORData(url):
    headers = {"accept" : "application/json"}
    try:
        cderes = requests.get(url, headers=headers)
        if cderes.status_code == 200:
            return cderes.json()
        else:
            return "error"
    except requests.exceptions.HTTPError as e:
       print(e)

def fetchRORData(file, url):
    #local_file=dir+file
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def makeDF(filename):
    if ".csv" in filename:
        #Build a dataframe from csv
        type = 'csv'
        ror_df = pd.read_csv(filename)
        return type, ror_df
    elif ".json" in filename:
        #Buld a datafram from json
        type = 'json'
        ror_df = pd.read_json(filename)
        return type, ror_df
    else:
        ror_df = pd.DataFrame()
        type = None
        return type, ror_df
    
def getCountryDF(countrycode, df):
    country_df = df[df['locations.geonames_details.country_code'] == countrycode]
    return country_df

def getNamesJSON(countrycode, df):
    namelist = []
    for index, row in df.iterrows():
        locations = row['locations']
        for location in locations:
            if location['geonames_details']['country_code'] == countrycode:
                for name in row['names']:
                    if "ror_display" in name['types']:
                        namelist.append(name['value'])
    return namelist

def main(args):
    #ROR downloads seem to take two steps.  Step 1 is to find out what the latest version is
    # Only download if no filename is provided
    localfile = None
    readfile = None

    #If no file name is provided, assume that we want to go get the latest version
    if args.filename is None:
        versionURL = "https://zenodo.org/api/communities/ror-data/records?q=&sort=newest"
        versionjson = getRORData(versionURL)

        #According to ROR, the latest revord is always "hits.hits[0]" and hte lastest file can be found at "hits.hit[0].files"
        latestrecord = versionjson['hits']['hits'][0]
        lastetfile = versionjson['hits']['hits'][0]['files']
        downloadurl = versionjson['hits']['hits'][0]['files'][0]['links']['self']
        filestring = downloadurl.split("/")
        filename = filestring[-2]
        if args.verbose:
            print(f"Latest Record:\n{latestrecord}")
            print(f"Latest File:\n{lastetfile}")
            print(f"DownnloadURL:\t{downloadurl}")
            print(f"File Name:\t{filename}")
        #Now that we have the info, time to go get the file.
        datadir = "/home/pihl/rordata/"
        localfile = datadir+filename
        fetchRORData(localfile, downloadurl)
    else:
        localfile = args.filename

    # And now to parse the file.  If the file is a .zip, need to unpack it first
    if '.zip' in localfile:
        pathlist = os.path.split(localfile)
        path = pathlist[0]
        file = pathlist[1]
        with zipfile.ZipFile(localfile, 'r') as z:
            z.extractall(path)
        #Now get the v2 json file
        f = []
        for (dirpath, dirnames, filename) in walk(path):
            f.extend(filename)
        if args.verbose:
            print(f"File Names:\t{f}")
            print(f"Dirpath:\t{dirpath}")
            print(f"Dirnames:\t{dirnames}")

        #Default to using the JSON file since it's the official record
        for file in f:
            if 'v2.json' in file:
                localfile = dirpath+"/"+file
    else:
        if 'v2' not in localfile:
            print("DANGER WILL ROBINSON!  This file does not appear to be a V2 schema ROR file.  This program will die miserably or produce strange results if this is not a V2 schema file.")
        elif ' .csv' in localfile:
            print("WARNING:  Parsing the csv file which ROR says is incomplete compared to the JSON file")
        
    #And now to create a dataframe
    dftype, ror_df = makeDF(localfile)
    #The CSV parse is pretty straight forward
    if dftype == 'csv':
        country_df = getCountryDF('US', ror_df)
        namelist = country_df['names.types.ror_display'].unique()
    elif dftype == 'json':
        namelist = getNamesJSON('US', ror_df)

    #Lastly write the namelist to a text file
    with open(args.output, 'w') as f:
        for name in namelist:
            f.write(f"{name}\n")

    
    
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-f", "--filename", default=None, help='File name to parse')
    parser.add_argument("-o", "--output", help="Full file to list names")


    args = parser.parse_args()

    main(args)