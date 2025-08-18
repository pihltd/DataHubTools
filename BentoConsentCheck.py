import argparse
import requests
import json
import pandas as pd


# Print iterations progress
# https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def runSSTRQuery(phs, page):
    pagesize = 250
    headers = {"accept" : "application/json"}
    sstr_url = f"https://www.ncbi.nlm.nih.gov/gap/sstr/api/v1/study/{phs}/subjects?page={page}&page_size={pagesize}"
    jsonresults = requests.get(sstr_url, headers=headers)
    return jsonresults.json()



def runBentoAPIQuery(url, query, variables=None):

    headers = {'accept': 'application/json'}
    try:
        if variables is None:
            results = requests.post(url, headers=headers, json={'query': query})
        else:
            results = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
    except requests.exceptions.HTTPError as e:
        return (f"HTTPError:\n{e}")
        
    if results.status_code == 200:
        if 'errors' in results:
            # GC has a connection bug where it fails the first time, but works the second
            runBentoAPIQuery(url, query, variables)
        else:
            results = json.loads(results.content.decode())
            return results
    else:
        return (f"Error Code: {results.status_code}\n{results.content}")



def getPHS(url):
    phslist = []
    phsquery = """
    {
        studies(
            study_names: [],
            study_acronyms: [],
            phs_accessions: [],
            offset: 0,
            first: 100
        ){
            study_name
            study_acronym
            phs_accession
        }
    }
    """
    res = runBentoAPIQuery(url, phsquery)
    #print(res)
    
    for entry in res['data']['studies']:
        phslist.append(entry['phs_accession'])  
    return phslist  


def buildBentoDF(url, phs, queryroot, dc, verbose = False):
    bento_df = pd.DataFrame(columns=["participant_id", "dbGaP_subject_id", "phs_accession"])
    
    if "." in phs:
        phslist = phs.split('.')
        phs = phslist[0]
     
    gcquery = """
        query phsCases($phs: String!, $offset: Int!, $first: Int!){
            participants(phs_accession: $phs, offset: $offset, first: $first){
                participant_id
                dbGaP_subject_id
                phs_accession
            }
        }
    """
    
    ctdcquery = """
      query ctdcCases($offset: Int!, $first: Int!){
          participantOverview(offset: $offset, first: $first){
              participant_id
          }
      }
    """
    
    offset = 0
    first = 100
    
    
    if dc == 'GC':
        query = gcquery
        variables = {"phs": phs, "offset": offset, "first": first}
    elif dc == 'CTDC':
        query = ctdcquery
        variables = {"offset": offset, "first": first}
    
    
    
    #bentoqueryres = runBentoAPIQuery(url, casequery, variables)
    bentoqueryres = runBentoAPIQuery(url, query, variables)
    #if bentoqueryres['data']['participants'] is None:
    print(bentoqueryres)
    if bentoqueryres['data'][queryroot] is None:
        bentoqueryres = runBentoAPIQuery(url, query, variables)
    while len(bentoqueryres['data'][queryroot]) >= 1:
            offset = offset + len(bentoqueryres['data'][queryroot])
            for entry in bentoqueryres['data'][queryroot]:
                bento_df.loc[len(bento_df)] = entry
            variables = {"phs": phs, "offset": offset, "first": first}
            if verbose:
                print(f"PHS: {phs}\t Offset: {str(offset)}")
            bentoqueryres = runBentoAPIQuery(url, query, variables)
    return bento_df



def buildDbGaPDF(phs, verbose=False):
    # TODO: Build in pagination looping
    sstrcols = ["study_key", "phs", "submitted_subject_id", "dbgap_subject_id", "consent_code", "consent_abbreviation", "case_control", "has_image", "samples"]
    sstr_df = pd.DataFrame(columns=sstrcols)
    pagecounter = 1
    sstrqueryres = runSSTRQuery(phs, pagecounter)
    for entry in sstrqueryres['subjects']:
        sstr_df.loc[len(sstr_df)] = entry
    if 'pagination' in sstrqueryres:
        pagecount = sstrqueryres['pagination']['total']
    else:
        pagecount = 1
    
    # Progress bar
    # https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    
    #pagesize = 250
    if verbose:
        print(f"SSTR query for {phs}")
        printProgressBar(0,pagecount, prefix="Progress", suffix="Complete", length=50)
    while pagecounter <= pagecount:
        pagecounter = pagecounter + 1
        if verbose:
            printProgressBar(pagecounter,pagecount, prefix="Progress", suffix="Complete", length=50)
        sstrqueryres = runSSTRQuery(phs, pagecounter)
        for entry in sstrqueryres['subjects']:
            sstr_df.loc[len(sstr_df)] = entry
    
    return sstr_df



def buildFiledbGaPDF(sstrfile, phs):
    sstr_df = pd.read_csv(sstrfile, sep="\t")
    sstr_df = sstr_df.rename(columns={'SUBJECT_ID':'submitted_subject_id', 'CONSENT':'consent_code'})
    sstr_df['phs_accession'] = phs
    return sstr_df

def buildComparisonDF(bento_df, sstr_df, samplesearch=False):
    finalcols = ["participant_id", "dbgap_subject_id", "consent_code", "consent_abbreviation", "phs_accession"]
    final_df = pd.DataFrame(columns=finalcols)
    if samplesearch:
        print('SEARCHING SAMPLES')
        searchkey = 'SAMPLE_ID'
    else:
        searchkey = 'submitted_subject_id'
    
    
    for index, row in bento_df.iterrows():
        dbgindex = sstr_df.index[sstr_df[searchkey] == row['participant_id']]
        if len(sstr_df['dbgap_subject_id'].values[dbgindex]) >= 1:
            dbgid = sstr_df['dbgap_subject_id'].values[dbgindex][0]
            code = sstr_df['consent_code'].values[dbgindex][0]
            abbrev = sstr_df['consent_abbreviation'].values[dbgindex][0]
        else:
            dbgid = 'N/A'
            code = 'N/A'
            abbrev = 'N/A'
        final_df.loc[len(final_df)] = {"participant_id": row['participant_id'], "dbgap_subject_id": dbgid,
                                       "consent_code": code, "consent_abbreviation": abbrev, "phs_accession": row['phs_accession']}
    return final_df
    
    

def main(args):
    cdsurl =' https://general.datacommons.cancer.gov/v1/graphql/'
    ctdcurl = 'https://clinical.datacommons.cancer.gov/v1/graphql/'
    #phs = args.phs
    print (f"Args: {args}")
    if args.phs == 'all':
        
        phslist = getPHS(cdsurl)
    else:
        phslist=[args.phs]

    for phs in phslist:
        
        if args.verbose:
            print(f"Working on {phs}")
        if args.sstrfile is not None:
            print(f"Using file {args.sstrfile}")
        if args.usesamples:
            print("Will search against sample IDs")
        
        #Hit the GC API for the participants in the study
        #bento_df = buildBentoDF(cdsurl, phs, args.verbose)
        bento_df = buildBentoDF(ctdcurl, phs, 'participantOverview', 'CTDC', args.verbose)
        
        if args.sstrfile is None:
            if args.verbose:
                print("Using SSTR API")
            #Hit the SSTR endpoint for the dbGaP info
            sstr_df = buildDbGaPDF(phs, args.verbose)
        else:
            if args.verbose:
                print(f"Using file {args.sstrfile}")
            sstr_df = buildFiledbGaPDF(args.sstrfile,phs)
        
        #build the comparison DF
        final_df = buildComparisonDF(bento_df, sstr_df, args.usesamples)

        #Write the results
        outputpath = r"C:\Users\pihltd\Documents\ConsentCodes"
        outputfile = outputpath+"\\"+phs+"_ctdc_test.csv"
        if args.verbose:
            print(f"Writing to {outputfile}")
        final_df.to_csv(outputfile, sep="\t")
        
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--phs",  required=True, help="phs number to check. Version suggested. Use 'all' to get all studies in GC.")
    parser.add_argument("-f", "--sstrfile", help='Use the provided SSTR file instead of the SSTR API')
    parser.add_argument("-s", "--usesamples", action='store_true', help='Search against dbGaP Sample ID instead of patient ID')
    parser.add_argument("-v", "--verbose", action='store_true', help='Verbose output')
        
    args = parser.parse_args()
    main(args)