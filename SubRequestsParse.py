#Parser for making a text file of a JSON dump from the DataHub submission requests database
import argparse
import pandas as pd
import json
import pprint

def main(args):
    with open(args.jsonfile,'r') as f:
        dbjson = json.load(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--jsonfile", required=True,  help="JSON file from database")

    args = parser.parse_args()

    main(args)