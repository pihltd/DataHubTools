#read one of he CDS Excel based submission sheets and generate the collection of DataHub submission files
import pandas as pd
import argparse
import yaml


def readConfigs(yamlfile):
    with open(yamlfile) as f:
        configs = yaml.load(f, Loader=yaml.FullLoader)
    return configs

def buildDict(modeldict):
    #Builds a dictionary of dataframes.  The key is the DH sheet, the value is the list of fields for that sheet
    df_dict = {}
    for key, fields in modeldict.items():
        df_dict[key] = pd.DataFrame(columns=fields)
    return df_dict

def checkExact(field, exact):
    #exact should be a list
    if field in exact:
        return True

def checkPartial(field, partial):
    #partial should be a list of dictionary with the DH values as keys.
    answer = False
    for entry in partial:
        if field in entry:
            answer = True
    return answer

def populateExact(sheet, dhfield, dhsheets, metadata_df):
    #Query the CDS dataframe for the value
    datalist = metadata_df[dhfield].to_list()

    #load the list into the correct df
    dhsheets[sheet].loc[:, dhfield] = datalist

def populatePartial(sheet, dhfield, cdsfield, dhsheets, metadata_df):
    datalist = metadata_df[cdsfield].to_list()
    dhsheets[sheet].loc[:,dhfield] = datalist

def main(args):
    #Read the config file
    configs = readConfigs(args.configfile)
    mappings = readConfigs(args.mappingfile)


    #Build a dataframe from the original CDS submission sheet
    Excel_df = pd.ExcelFile(configs['Ops']['input_file'])
    metadata_df = pd.read_excel(Excel_df, 'Metadata')

    #Build a dictionary of dataframes.  These are the individual DH manifests
    dhsheets = buildDict(configs['Templates'])


    #Read the mappings and get the exact and partial mappings
    dh_exact = mappings['Exact']
    dh_partial = mappings['Partial']
    dh_manual = mappings['Manual']

    #For each of the DH sheets, we need to get the mappings to the CDS sheet and then load the data from the CDS sheet into the DH sheet

    for sheet, fieldlist in dhsheets.items():
        #Work each of the DH fields and determin if an exact match or a partial map
        for field in fieldlist:
            if sheet in dh_exact:
                if checkExact(field, dh_exact[sheet]):
                    #Populate the column
                    populateExact(sheet, field, dhsheets, metadata_df)
            if sheet in dh_partial:
                if checkPartial(field, dh_partial[sheet]):
                    for entry in dh_partial[sheet]:
                        if field in entry:
                            populatePartial(sheet, field, entry[field], dhsheets, metadata_df)
            #Manual mapped uses same format as partial, so can use saem approach
            if sheet in dh_manual:
                if checkPartial(field, dh_manual[sheet]):
                    for entry in dh_manual[sheet]:
                        if field in entry:
                            populatePartial(sheet, field, entry[field], dhsheets, metadata_df)

    #At this point we should have populated everything we can, time to remove duplicate rows in the dataframes
    for sheet, sheet_df in dhsheets.items():
        dhsheets[sheet] = sheet_df.drop_duplicates()

    #Put the sheet name in the first row of the type column
    for sheet, sheet_df in dhsheets.items():
        sheet_df.loc[0,'type'] = sheet

    for sheet, df in dhsheets.items():
        filename = configs['Ops']['output_path']+configs['Ops']['output_prefix']+sheet+".tsv"
        df.to_csv(filename, sep="\t", index=False)
    

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--configfile", required=True,  help="Configuration file containing all the input info")
    parser.add_argument("-m", "--mappingfile", required=True, help="Data Model to Submission mapping file")

    args = parser.parse_args()

    main(args)