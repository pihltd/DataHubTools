import yaml
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
import argparse

def readYaml(yamlfile):
    with open(yamlfile) as f:
        jsonstuff = yaml.load(f, Loader=yaml.FullLoader)
    return jsonstuff

def main(args):
    modelyaml = "/home/pihl/models/cds-model/model-desc/cds-model.yml"
    propyaml = "/home/pihl/models/cds-model/model-desc/cds-model-props.yml"
    testxls = "/home/pihl/Documents/test_submission.xlsx"

    modelyaml = args.modelfile
    propyaml = args.propsfile

    model = readYaml(modelyaml)
    props = readYaml(propyaml)


    wb = Workbook()
    wb.remove(wb.active)

    for node, nodeinfo in model['Nodes'].items():
        row = 1
        col = 1
        proplist = nodeinfo['Props']
        ws = wb.create_sheet(node)
        enums = {}
        for prop in proplist:
            #Write the column header
            ws.cell(row=row, column=col).value = prop
            if(args.validation):
                #Check and see if the property has enumerated values
                if 'Enum' in props['PropDefinitions'][prop]:
                    #There are enums let's write a data validation
                    #ws.cell(row = 2, column=col, value=props['PropDefinitions'][prop]['Enum'])
                    #print(props['PropDefinitions'][prop]['Enum'])
                    #print(type(props['PropDefinitions'][prop]['Enum']))
                    dv = DataValidation(type='list', formula1=props['PropDefinitions'][prop]['Enum'], allow_blank=True, showDropDown=True)
                    column = get_column_letter(col)
                    #maxrow = ws.max_row()
                    maxrow = 1048576
                    #colrange = column+'2:'+str(maxrow)
                    colrange = "{}2:{}{}".format(column, column, str(maxrow))
                    #print(colrange)
                    #dv.range.append(colrange)
                    dv.add(colrange)
                    ws.add_data_validation(dv)

            col = col +1
    #print(args.outputfile)
    wb.save(args.outputfile)
    wb.close()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--modelfile", required=True, help="MDF model file")
    parser.add_argument("-p", "--propsfile", required=True, help="MDF Properties file")
    parser.add_argument("-o", "--outputfile", required=True, help="Output spreadsheet")
    parser.add_argument("-v", "--validation", action='store_true', help="Create workbook with column validation")
        
    args = parser.parse_args()
    main(args)
    