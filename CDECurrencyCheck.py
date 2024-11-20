#Checks the CDEs in an MDF file to see if they are still current or have been retired.  Also checks to see if there is an updated version

import bento_mdf
from crdclib import crdclib as crdc
import pandas as pd
import argparse


def getNewCDEInfo(cdeid):
    # Get the current status and version for a cde
    cderecord = crdc.getCDERecord(cdeid)
    if cderecord['status'] == 'success':
        cdestatus = cderecord['DataElement']['workflowStatus']
        latest = cderecord['DataElement']['latestVersionIndicator']
        version = cderecord['DataElement']['version']
        recordid = cderecord['DataElement']['publicId']
        return {"status": cdestatus, "version": version, "cdeid": recordid, "latest": latest}
    else:
        return{"Error": cderecord}


def main(args):
    
    configs = crdc.readYAML(args.configfile)
    columns = ("cde_name", "cde_id", "cde_version", "cde_status", "latest_version", "latest_version_indicator")
    report_df = pd.DataFrame(columns=columns)
    
    mdffiles = configs['mdffiles']
    mdfmodel = bento_mdf.MDF(*mdffiles)
    
    #GEt the properties
    props = mdfmodel.model.props
    # This is a list of tuples that can be used to get individual props
    proplist = list(props.keys())
    
    for node, prop in proplist:
        #need to get the CDE ID, name, and version
        if mdfmodel.model.props[(node,prop)].concept is not None:
            propterms = mdfmodel.model.props[(node,prop)].concept.terms
            for termobject in propterms.values():
           # for termsourcekey, termobject in propterms.items():
                termdict = termobject.get_attr_dict()
                cdeid = termdict['origin_id']
                cdeversion = termdict['origin_version']
                cdename = termdict['value']
                newinfo = getNewCDEInfo(cdeid)
                if "Error" not in newinfo.keys():
                    report_df.loc[len(report_df)] = {"cde_name": cdename, "cde_id": cdeid, "cde_version": cdeversion,
                                                    "cde_status": newinfo['status'], "latest_version": newinfo['version'],
                                                    "latest_version_indicator": newinfo['latest']}
    
    report_df.to_csv(configs['outputfile'], sep="\t", index=False)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")

    args = parser.parse_args()

    main(args)