#Queries the dbGaP SSTR API (Subject Sample Telemetry Report) and parses out patient and sample IDs

import argparse
import requests
import pandas as pd
import sys
from crdclib import crdclib


def runQuery(phs, page):
    headers = {"accept" : "application/json"}
    sstr_url = f"https://www.ncbi.nlm.nih.gov/gap/sstr/api/v1/study/{phs}/subjects?page={page}&page_size=25"
    jsonresults = requests.get(sstr_url, headers=headers)
    return jsonresults.json()

def getdbGaPInfo(phs, testrun, verbose = 0):
    pagenum = 1
    dbgaplist = []
    phsres = runQuery(phs, pagenum)
    totalpages = phsres['pagination']['total']
    if testrun:
        totalpages = 3
    dbgaplist = dbgaplist+phsres['subjects']
    if verbose >=1:
        print(f"Lenght of dbgaplist: {len(dbgaplist)}")
    pagenum = 2
    while pagenum <= totalpages:
        if verbose >= 1:
            print(f"Getting page {pagenum} of {totalpages}")
        phsres = runQuery(phs, pagenum)
        dbgaplist = dbgaplist+phsres['subjects']
        if verbose >=1:
            print(f"Lenght of dbgaplist: {len(dbgaplist)}")
        pagenum = pagenum + 1
    df = pd.DataFrame(dbgaplist)
    if testrun:
        print(df)
    return df


def getSubmittedConsentAbbreviation(participant_id, submitted_df):
    temp_df = submitted_df.query('participant_id == @participant_id')
    if len(temp_df) != 1:
        print(f"ID {participant_id} has multiple consent codes")
        print(temp_df)
        sys.exit(0)
    else:
        return temp_df.iloc[0]['consent_group_name'], temp_df.iloc[0]['consent_group_number']

def compareDF(mapping_df, dbgap_df, submitted_df):
    results = []
    for index, row in mapping_df.iterrows():
        searchid = row['dbGaP subject ID']
        kf_id = row['KF ID']
        found_df = dbgap_df.query('submitted_subject_id == @searchid')
        if not found_df.empty:
            for findex, frow in found_df.iterrows():
                dbgapcc = frow['consent_abbreviation']
                subcc, subccn = getSubmittedConsentAbbreviation(kf_id, submitted_df)
                if dbgapcc == subcc:
                    results.append({"dbgap_submitted_subject_id": frow['submitted_subject_id'], "GC_kf_id": row['KF ID'], 'dbgap_consent_code': frow['consent_code'], 'dbgap_consent_abbreviation': frow['consent_abbreviation'], 'GC_consent_code': subccn, 'GC_consent_abbreviation': subcc, 'status': 'Match'})
                else:
                    results.append({"dbgap_submitted_subject_id": frow['submitted_subject_id'], "GC_kf_id": row['KF ID'], 'dbgap_consent_code': frow['consent_code'], 'dbgap_consent_abbreviation': frow['consent_abbreviation'], 'GC_consent_code': subccn, 'GC_consent_abbreviation': subcc, 'status': 'CONSENT MISMATCH'})
        else:
            #results.append({"submitted_subject_id": searchid, "kf_id": row['KF ID'], 'consent_code': None, 'consent_abbreviation': None, 'status': 'NO MATCH'})
            results.append({"dbgap_submitted_subject_id": searchid, "GC_kf_id": row['KF ID'], 'dbgap_consent_code': None, 'dbgap_consent_abbreviation': None, 'GC_consent_code': subccn, 'GC_consent_abbreviation': subcc, 'status': 'PATIENT ID NOT FOUND'})
    df = pd.DataFrame(results)
    return df


def updateSubmittedInfo(submitted_df, consent_df):
    # Adds consent group info to the participant load sheet
    columns = submitted_df.columns.tolist()
    columns.append("consent_group_number")
    columns.append("consent_group_name")
    new_df = pd.DataFrame(columns=columns)
    for index, row in submitted_df.iterrows():
        rowdict = submitted_df.iloc[index].to_dict()
        id = row['consent_group.consent_group_id']
        temp_df = consent_df.query('consent_group_id == @id')
        if len(temp_df) != 1:
            print("Consent group mapping error, more than one mapping")
            sys.exit(0)
        else:
            rowdict['consent_group_number'] = str(temp_df.iloc[0]['consent_group_number'])
            rowdict['consent_group_name'] = temp_df.iloc[0]['consent_group_name']
            new_df.loc[len(new_df)] = rowdict
    return new_df





def main(args):
    configs = crdclib.readYAML(args.configfile)

    # Stargin dataframes
    mapping_df = pd.read_csv(configs['mapping_file'], sep=",")
    submitted_df = pd.read_csv(configs['submitted_file'], sep="\t")
    consent_df = pd.read_csv(configs['consent_file'], sep="\t")

    submitted_df = updateSubmittedInfo(submitted_df, consent_df)


    #Get the info from SSTR or SSTR File
    if configs['sstrfile'] is not None:
        if args.verbose >= 1:
            print(f"Reading dbGaP info from {configs['sstrfile']}")
        dbgap_df = pd.read_csv(configs['sstrfile'], sep="\t")
    else:
        if args.verbose >= 1:
            print("Getting dbGaP Infor from SSTR API")
        dbgap_df = getdbGaPInfo(configs['phs'], configs['testrun'], args.verbose)
        if args.verbose >= 1:
            print(f"Saving dbGaP info to {configs['dbgapinfo_file']}")
        dbgap_df.to_csv(configs['dbgapinfo_file'], sep="\t")

    #compare mapping to dbgap
    if args.verbose >= 1:
        print("Starting Participant ID Comparison")
    check_df = compareDF(mapping_df=mapping_df, dbgap_df=dbgap_df, submitted_df=submitted_df)
    if args.verbose >= 1:
        print(f"Writing comparison report to {configs['report_file']}")
    check_df.to_csv(configs['report_file'], sep="\t")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True, help="YAML configuration file")
    parser.add_argument('-v', '--verbose', action='count', default=0, help=("Verbosity: -v main section -vv subroutine messages -vvv data returned shown"))
        
    args = parser.parse_args()
    main(args)

