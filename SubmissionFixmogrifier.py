# Attempts to fix a variety of common DH submisison sheet flaws
# Directions supplied in a yaml file
import argparse
from crdclib import crdclib
import pandas as pd
import uuid
import sys



def dfcheck(node, nodesdf):
    testdf = nodesdf[node]
    print(f"Node:{node}\nColumns: {testdf.columns.to_list()}")



def buildNodeDF(filename, node, finaldfs, separator):
    if separator == 'comma':
        df = pd.read_csv(filename, sep=",")
    elif separator == 'tab':
        df = pd.read_csv(filename, sep="\t")
    else:
        print("Source file separator unknown, please specify in config file")
        sys.exit(0)
    df.astype(str)
    finaldfs[node] = df
    return finaldfs



def addFileID(nodesdf, infodict):
    fp = 'dg.4DFC/'
    file_df = nodesdf['file']
    for index, row in file_df.iterrows():
        file_df.loc[index, infodict['file']] = fp+str(uuid.uuid4())
    nodesdf['file'] = file_df
    return nodesdf



def getPHS(phsnode, phsfield, nodesdf, default):
    if phsfield is None:
        return default
    else:
        df = nodesdf[phsnode]
        phslist = df[phsfield].unique()
        if str(phslist[0]) == 'nan':
            return default
        else:
            return phslist[0]

    

def addPHS(nodesdf, node, infodict, defaultphs):
    if 'study' in nodesdf:
        phsnum = getPHS('study',infodict['study'], nodesdf, defaultphs )
    else:
        phsnum = getPHS('study',None, nodesdf, defaultphs )
    working_df = nodesdf[node]
    for index, row in working_df.iterrows():
        working_df.loc[index, infodict['participant']] = phsnum
    nodesdf[node] = working_df
    return nodesdf
    
    
    
def makeStudyParticipantID(nodesdf, infodict, defaultphs):
    studyphs = getPHS('study','phs_accession', nodesdf, defaultphs )
    for node, field in infodict.items():
        working_df = nodesdf[node]
        for index, row in working_df.iterrows():
            if row['study.phs_accession'] is not None:
                studyparticipantid = row['study.phs_accession']+"_"+row['participant_id']
            else:
                studyparticipantid = studyphs+"_"+row['participant_id']
            working_df.loc[index, field] = studyparticipantid
        nodesdf[node] = working_df
    return nodesdf



def makePrimaryDiagnosis_id(nodesdf, infodict):
    diagnosis_df = nodesdf['diagnosis']
    for index, row in diagnosis_df.iterrows():
        diag_id = str(row[infodict['diagnosis']])+"_"+str(row[infodict['site']])+"_"+str(index)
        diagnosis_df.loc[index, infodict['idfield']] = diag_id
    nodesdf['diagnosis'] = diagnosis_df
    return nodesdf



def makeStudyDiagnosisID(nodesdf, infodict):
    diagnosis_df = nodesdf['diagnosis']
    for index, row in diagnosis_df.iterrows():
        sdi = row[infodict['diagnosis']]+"_"+row[infodict['participant']]
        diagnosis_df.loc[index, infodict['idfield']] = sdi
    nodesdf['diagnosis'] = diagnosis_df
    return nodesdf



def addUUID(nodesdf, node, targetfield):
    working_df = nodesdf[node]
    for index, row in working_df.iterrows():
       working_df.loc[index, targetfield] = str(uuid.uuid4())
    nodesdf[node] = working_df
    return nodesdf



def participantIdStudyParticipantIDIndex(participant_df, infodict):
    id_index = {}
    for index, row in participant_df.iterrows():
        id_index[row[infodict['refpartid']]] = row[infodict['refstudypartid']]
    return id_index



def updateStudyParticipantID(nodesdf, node, infodict, mapping):
    working_df = nodesdf[node]
    for index, row in working_df.iterrows():
        startkey = row[infodict['idfield']]
        if startkey in mapping:
            newvalue = mapping[startkey]
            working_df.loc[index, infodict['idfield']] = newvalue
        else:
            working_df.loc[index, infodict['idfield']] = f"Identifier Not Found: {startkey}"
    nodesdf[node] = working_df
    return nodesdf
    
    

def main(args):
    configs = crdclib.readYAML(args.configfile)
        
    #Create a dictionary of dataframes.  One for each loading sheet
    nodesdf = {}
    for entry in configs['submissionfiles']:
        for node, filename in entry.items():
            nodesdf = buildNodeDF(filename, node, nodesdf, configs['separator'])
    if args.verbose:
        for node, df, in nodesdf.items():
            print(f"Node: {node}\tDataFrame: \n{df.columns.tolist()}")
    
    fixthis = configs['fixes']
    
    #Available fixes
    # fileid - populates the file_id column of the file node
    # participantphs: Adds the study phs number to the participant sheet
    # study_participant_id: Creates the study_participant_id and populates the column
    # diagnosis_id
    # study_diagnosis_id:  Creates a study_diagnosis_id 
    
    
    if 'fileid' in fixthis.keys():
        if args.verbose:
            print('Adding file ids')
        nodesdf = addFileID(nodesdf, fixthis['fileid'])
    if 'addphs' in fixthis.keys():
        if args.verbose:
            print('Adding phs number')
        infodict = fixthis['addphs']
        nodes = infodict['nodes']
        for node in nodes:
            print(f"Sending {node} to addPHS")
            nodesdf = addPHS(nodesdf, node, infodict, fixthis['phs'])
            dfcheck('participant', nodesdf)
    if 'study_participant_id' in fixthis.keys():
        if args.verbose:
            print('Adding study participant ID')
        nodesdf = makeStudyParticipantID(nodesdf, fixthis['study_participant_id'], fixthis['phs'])
    if 'diagnosis_id' in fixthis.keys():
        if args.verbose:
            print('Adding diagnosis ID')
        nodesdf = makePrimaryDiagnosis_id(nodesdf, fixthis['diagnosis_id'])
    if 'study_diagnosis_id' in fixthis.keys():
        if args.verbose:
            print('Adding study diagnosis ID')
        nodesdf = makeStudyDiagnosisID(nodesdf, fixthis['study_diagnosis_id'])
    if 'add_uuid' in fixthis.keys():
        if args.verbose:
            print('Adding UUIDs')
        nodes = fixthis['add_uuid']['nodes']
        for node in nodes:
            if args.verbose:
                print(f"Adding UUID for node: {node}")
            for key, value in node.items():
                nodesdf = addUUID(nodesdf, key, value)
    if 'update_study_participant_id' in fixthis.keys():
        if args.verbose:
            print('Updating mistaken study participant id')
        infodict = fixthis['update_study_participant_id']
        nodes = infodict['nodes']
        mapping = participantIdStudyParticipantIDIndex(nodesdf[infodict['refnode']], infodict)
        for node in nodes:
            nodesdf = updateStudyParticipantID(nodesdf, node, infodict, mapping)
            
        
        
    # Write them all out
    for node, df in nodesdf.items():
        filename = configs['outputdir']+node+".tsv"
        df.to_csv(filename, sep="\t", index=False)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")
    parser.add_argument("-v", "--verbose", action='store_true', help="Verbose Output")

    args = parser.parse_args()

    main(args)