#Adds the latest version number for a CDE ID to MDF property files
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

def runQuery(cdeid):
    headers = {"accept" : "application/json"}
    url = f"https://cadsrapi.cancer.gov/rad/NCIAPI/1.0/api/DataElement/{cdeid}"
    try:
        cderes = requests.get(url, headers=headers)
        if cderes.status_code == 200:
            return cderes.json()
        else:
            return "error"
    except requests.exceptions.HTTPError as e:
       print(e)

def parseVersion(cdejson):
    version = cdejson['DataElement']['version']
    return version

def checkIt(original, changed):
    #Check if changed has all the original properties
    oldprops = original.keys()
    for oldprop in oldprops:
        if oldprop not in changed:
            print(f"Property {oldprop} not found in new file")
    print("Validation complete")


def main(args):
    newprops = {}
    propjson = readYaml(args.propfile)
    propjson = propjson['PropDefinitions']
    for property, propinfo in propjson.items():
        #CDEs are in the Term section
        if "Term" in propinfo:
            #Check if this is a caDSR CDE
            newterm = []
            for entry in propinfo['Term']:
                #print(entry)
                if "caDSR" in entry['Origin']:
                    #Need to check if entry[Code] is an integer first
                    if 'Code' in entry:
                        if entry['Code'] != 'code/ID':
                            cdeinfo = runQuery(entry['Code'])
                            cdeversion = parseVersion(cdeinfo)
                            entry['Version'] = cdeversion
                            newterm.append(entry)
                        else:
                            newterm.append(entry)
                    else:
                        newterm.append(entry)
                else:
                    newterm.append(entry)
                propinfo['Term'] = newterm
        #Add the property back to the corrected version
        newprops[property] = propinfo

    #Validation option
    if args.validate:
        checkIt(propjson, newprops)

    #Write it all out
    newerprops = {}
    newerprops['PropDefinitions'] = newprops
    writeYAML("/home/pihl/Documents/CTDC_Versioned.yml", newerprops)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--propfile", required=True,  help="MDF Property file containing CDE IDs and versions")
    parser.add_argument("-v", "--validate", action='store_true', help="Run validation")

    args = parser.parse_args()

    main(args)