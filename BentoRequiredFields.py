import yaml
import argparse

def readYaml(yamlfile):
    with open(yamlfile) as f:
        jsonstuff = yaml.load(f, Loader=yaml.FullLoader)
    return jsonstuff

def main(args):
    modelfile = "/media/vmshare/cds-model.yml"
    propsfile = "/media/vmshare/cds-model-props.yml"
    outfile = "/media/vmshare/cds-required-properties.yml"

    modeljson = readYaml(modelfile)
    propjson = readYaml(propsfile)
    propjson = propjson['PropDefinitions']

    finaljson = {}

    for node, nodedata in modeljson['Nodes'].items():
        proplist = nodedata['Props']
        temp = []
        for prop in proplist:
            #print(propjson[prop])
            if 'Req' in propjson[prop]:
                #print(propjson[prop]['Req'])
                #print(type(propjson[prop]['Req']))
                if propjson[prop]['Req']:
                #if propjson[prop]['Req'] == 'True':
                    temp.append(prop)
        finaljson[node] = temp

    with open(outfile, "w") as f:
        yaml.dump(finaljson, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose",  help="Verbose Feedback")
        
    args = parser.parse_args()
    main(args)