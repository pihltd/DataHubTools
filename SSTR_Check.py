#Queries the dbGaP SSTR API (Subject Sample Telemetry Report) and parses out patient and sample IDs

import argparse
import requests
import re
import sys
import pprint
import pandas as pd
import csv
import yaml

def phsCheck(phsnum):
    #regex  ^phs\d{6}\.v\d?\d$
    fullp = re.compile('^phs\d{6}\.v\d?\d$', re.IGNORECASE)
    partp = re.compile('^phs\d{6}', re.IGNORECASE)
    if fullp.match(phsnum):
        return True
    elif partp.match(phsnum):
        return True
    else:
        return False
                   
def runQuery(phs, page):
    headers = {"accept" : "application/json"}
    sstr_url = f"https://www.ncbi.nlm.nih.gov/gap/sstr/api/v1/study/{phs}/subjects?page={page}&page_size=25"
    jsonresults = requests.get(sstr_url, headers=headers)
    return jsonresults.json()

def appendDF(df, jsonresults):
    for subject in jsonresults['subjects']:
        dbgap_subject_id = subject['dbgap_subject_id']
        submitted_subject_id = subject['submitted_subject_id']
        for sample in subject['samples']:
            submitted_sample_id = sample['submitted_sample_id']
            dbgap_sample_id = sample['dbgap_sample_id']
            biosample_id = sample['biosample_id']
            temp = {'submitted_subject_id' : submitted_subject_id,
                    'dbgap_subject_id' : dbgap_subject_id,
                    'submitted_sample_id' : submitted_sample_id,
                    'dbgap_sample_id' : dbgap_sample_id,
                    'biosample_id' : biosample_id}
            #df2 = pd.DataFrame(temp)
            df = df._append(temp, ignore_index = True)
    return df

def searchDF(df, column, value):
    if value in df[column]:
        return True
    else:
        return False
    
def parseLoadsheet(loadsheet):
    final = {} #Key is participant id, value is list of samples
    with open(loadsheet, 'r') as f:
        reader = csv.reader(f, delimiter="\t", quotechar='"')
        headers = next(reader)
        participantid = headers.index('participant.study_participant_id')
        sampleid = headers.index('sample_id')
        for row in reader:
            if row[participantid] in final:
                temp = final[row[participantid]]
                temp.append(row[sampleid])
                final[row[participantid]] = temp
            else:
                temp = []
                temp.append(row[sampleid])
                final[row[participantid]] = temp
    return final

def getdbGaPInfo(df, phs, testrun):
    pagenum = 1
    phsres = runQuery(phs, pagenum)
    totalpages = phsres['pagination']['total']
    if testrun:
        totalpages = 3
    df = appendDF(df, phsres)
    pagenum = 2
    while pagenum <= totalpages:
        print(f"Getting page {pagenum} of {totalpages}")
        phsres = runQuery(args.phs, pagenum)
        df = appendDF(df, phsres)
        pagenum = pagenum + 1
    if testrun:
        print(df)
    return df

def writeYAML(filename, jsonthing):
    with open(filename, 'w') as f:
        yaml.dump(jsonthing, f)
    f.close()

def main(args):
    #Check to see that the phs number is formatted correctly
    if not phsCheck(args.phs):
        print(f"{args.phs} is not a valid phs number")
        sys.exit(0)
    
    columns = ['submitted_subject_id', 'dbgap_subject_id', 'submitted_sample_id', 'dbgap_sample_id', 'biosample_id']
    dbgap_df = pd.DataFrame(columns=columns)

    #Run the first query
    print("Get dbGaP Info")
    dbgap_df = getdbGaPInfo(dbgap_df, args.phs, args.testrun)
   
    submission = parseLoadsheet(args.samplesheet)
    #Start with a patient ID check, we may not need the sample check
    passed = {}
    failed = {}
    for patient, samples in submission.items():
        if searchDF(dbgap_df, 'submitted_subject_id', patient):
            passed[patient] = samples
        else: 
            failed[patient] = samples
    writeYAML('/home/pihl/Documents/PatIDCheckPass.yml', passed)
    writeYAML('/home/pihl/Documents/PatIDCheckFail.yml', failed)
    dbgap_df.to_csv('/home/pihl/Documents/dbGap.tsv', sep="\t")
    print("dbGaP Patient check complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--phs",  required=True, help="phs number to check. Version suggested")
    parser.add_argument("-t", "--testrun", action='store_true', help="Flag to run limited dbGaP queriers as test runs")
    parser.add_argument("-s", "--samplesheet", help="Sample load sheet")
        
    args = parser.parse_args()
    main(args)

