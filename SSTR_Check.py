#Queries the dbGaP SSTR API (Subject Sample Telemetry Report) and parses out patient and sample IDs

import argparse
import requests
import re
import sys
import pprint

def phsCheck(phsnum):
    #regex  ^phs\d{6}\.v\d?\d$
    p = re.compile('^phs\d{6}\.v\d?\d$', re.IGNORECASE)
    if p.match(phsnum):
        return True
    else:
        return False
                   
def runQuery(phs):
    headers = {"accept" : "application/json"}
    sstr_url = f"https://www.ncbi.nlm.nih.gov/gap/sstr/api/v1/study/{phs}/subjects?page=1&page_size=25"
    jsonresults = requests.get(sstr_url, headers=headers)
    return jsonresults.json()

def parsePatSamp(jsonresults):
    #Creates a dictionary with patient IDs and keys and samples from patients as list
    patsamp = {}
    for subject in jsonresults['subjects']:
        subject_id = subject['dbgap_subject_id']
        #pprint.pprint(subject_id)
        temp = []
        for sample in subject['samples']:
            temp.append(sample['dbgap_sample_id'])
        #pprint.pprint(temp)
        patsamp[subject_id] = temp
    return patsamp

def main(args):
    #Check to see that the phs number is formatted correctly
    if not phsCheck(args.phs):
        print(f"{args.phs} is not a valid phs number")
        sys.exit(0)
    
    phsres = runQuery(args.phs)
    validdata = parsePatSamp(phsres)
    pprint.pp(validdata)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--phs",  required=True, help="phs number to check.  Requires version number")
        
    args = parser.parse_args()
    main(args)

