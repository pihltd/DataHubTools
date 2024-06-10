# A basic python script to use a few different regular expressions to look for PII/PHI in text files
import argparse
import re
import yaml

def getRegEx(yamlfile):
    with open(yamlfile) as f:
        jsonstuff = yaml.load(f, Loader=yaml.FullLoader)
    jsonstuff = jsonstuff['RegEx']
    return jsonstuff

def checkPIIPHI(line, regstring):
    check = re.match(regstring, line)
    if check:
        return check
    else:
        return None

def main(args):

    regexstuff = getRegEx(args.configs)

    with open(args.inputfile) as f:
        linecount = 1
        for line in f:
            for regexname, regexinfo in regexstuff.items():
                check = checkPIIPHI(line, regexinfo['test'])
                if check is not None:
                    print(("Found %s on line %s") % (regexinfo['error', str(linecount)]))
            linecount = linecount + 1   
 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose",  help="Verbose Feedback")
    parser.add_argument("--c", "-configs", required=True, help="Configuraiton file wiht regular expressions")
    parser.add_argument("--f", "--inputfile", required=True, help="Text file to be searched for PII/PIHL")
        
    args = parser.parse_args()
    main(args)