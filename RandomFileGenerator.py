#Generate a random file of either binary or text
import argparse
from crdclib import crdclib
import random
import string
import os

def randomString(size):
    randomstring = ''.join([random.choice(string.ascii_letters) for i in range(size)])
    return randomstring

def randomBinary(size):
    randombytes = os.urandom(size)
    return randombytes


def main(args):
    configs = crdclib.readYAML(args.configfile)
    filelist = configs['file_names']
    for file in filelist:
        outputfile = configs['output_directory']+file
        print(f"Creating content for {file}")
        if configs['data_type'] == 'Text':
            content = randomString(configs['file_size'])
            with open (outputfile, "w") as f:
                f.write(content)
        elif configs['data_type'] == 'Binary':
            content = randomBinary(configs['file_size'])
            with open (outputfile, "wb") as f:
                f.write(content)
        else:
            content = None
        outputfile = configs['output_directory']+file
        print(f" Writing to file {outputfile}")
        
        
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")

    args = parser.parse_args()

    main(args)