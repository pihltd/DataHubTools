#Compares ENUM values from MDF to CDE PVs
import argparse
import requests
import yaml

def readYaml(yamlfile):
    with open(yamlfile) as f:
        configs = yaml.load(f, Loader=yaml.FullLoader)
    return configs

def writeYAML(filename, jsonthing):
    with open(filename, 'w') as f:
        yaml.dump(jsonthing, f)
    f.close()

def runQuery(cdeid, cdeversion):
    headers = {"accept" : "application/json"}
    url = f"https://cadsrapi.cancer.gov/rad/NCIAPI/1.0/api/DataElement/{cdeid}?version={cdeversion}"
    try:
        cderes = requests.get(url, headers=headers)
        if cderes.status_code == 200:
            return cderes.json()
        else:
            return "error"
    except requests.exceptions.HTTPError as e:
       print(e)

def cdePVList(cdejson):
    pvlist = []
    pvstuff = cdejson['DataElement']['ValueDomain']['PermissibleValues']
    for entry in pvstuff:
        pvlist.append(entry['value'])
    return pvlist


def main(args):
    propjson = readYaml(args.propfile)
    #Look for properties that have an ENUM section
    finaldata = {}
    mdfdata = {}
    cdedata = {}
    for prop, propdata in propjson['PropDefinitions'].items():
        if "Enum" in propdata:
            #Have to check if there is a Term section, not all Enums are coming from CDEs apparently
            if "Term" in propdata:
                mdfenumlist = propdata['Enum']
                mdfdata[prop] = mdfenumlist
                for entry in propdata['Term']:
                    cdeid = entry['Code']
                    cdever = entry['Version']
                    cdejson = runQuery(cdeid, cdever)
                    if cdejson == 'error':
                        finaldata[prop] = 'HTTP Error'
                    else:
                        temp = []
                        pvlist = cdePVList(cdejson)
                        cdedata[prop] = pvlist
                        #We're primarily insterested in MDF Enums that are not in the CDE PVs
                        for enum in mdfenumlist:
                            if enum not in pvlist:
                                temp.append(enum)
                        finaldata[prop] = temp

    thewholeenchilada = {}
    thewholeenchilada["MDF"] = mdfdata
    thewholeenchilada["CDE"] = cdedata
    thewholeenchilada["Final"] = finaldata

    
    writeYAML("Enum_compare.yml", thewholeenchilada)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--propfile", required=True,  help="MDF Property file containing CDE IDs and versions")

    args = parser.parse_args()

    main(args)