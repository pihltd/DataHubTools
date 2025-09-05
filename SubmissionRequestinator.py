#Note:  You need to log into Prod via a browser first for this to work.
import pandas
import requests
import sys


def apiQuery(query, variables, queryprint = False):
    '''
    if tier == 'DEV2':
        url = 'https://hub-dev2.datacommons.cancer.gov/api/graphql'
        token = os.environ['DEV2API']
    elif tier == 'STAGE':
        url = 'https://hub-stage.datacommons.cancer.gov/api/graphql'
        token = os.environ['STAGEAPI']
    elif tier == 'PROD':
        url = 'https://hub.datacommons.cancer.gov/api/graphql'
        token = os.environ['PRODAPI']
    elif tier == 'BUPKIS':
        return("The Bupkis tier has been selected")
    elif tier == None:
        return("No tier specified")
 '''  
    url = 'https://hub.datacommons.cancer.gov/api/graphql'

    #headers = {"Authorization": f"Bearer {token}"}
    
    try:
        result = requests.post(url=url, json={"query":query, "variables":variables})
        if result.status_code == 200:
            return result.json()
        else:
            print(f"Error: {result.status_code}")
            return result.content
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return f"HTTP Error: {e}"
    '''
    try:
        if variables is None:
            result = requests.post(url = url, headers = headers, json={"query": query})
            if queryprint:
                print(query)
        else:
            result = requests.post(url = url, headers = headers, json = {"query":query, "variables":variables})
            if queryprint:
                print(query)
                print(variables)
        if result.status_code == 200:
            return result.json()
        else:
            print(f"Error: {result.status_code}")
            return result.content
    except requests.exceptions.HTTPError as e:
        return(f"HTTP Error: {e}")
    '''
    
    



statuses = ["New", "In Progress", "Submitted", "In Reveiw", "Inquired", "Approved", "Rejected", "Canceled", "Deleted"]

reqquery = """
    query ListApplications(
        $statuses: [String]
    ){
        listApplications(statuses:$statuses){
    applications{
      _id
      studyName
      applicant{
        applicantName
      }
      studyAbbreviation
      submittedDate
      organization{
        name
      }
      status
      
      
    }
  }
    }

"""

queryvars = {"statuses": statuses}

reqjson = apiQuery(reqquery, queryvars)
#if 'Error' in reqjson:
#    print(reqjson)
#    sys.exit(0)

columns = ['Study Name', 'Applicant Name', 'Study Abbreviation', 'Submitted Date', 'Organization', 'Status']
app_df = pandas.DataFrame(columns=columns)

for app in reqjson['data']['listApplications']['applications']:
    #applicant = app['applicant']['applicantName']
    #org = app['organization']['name']
    app_df.loc[len(app_df)] = {'Study Name':app['studyName'],
                               'Applicant Name': app['applicant']['applicantName'],
                               'Study Abbreviation': app['studyAbbreviation'],
                               'Submitted Date':app['submittedDate'],
                               'Organization': app['organization']['name'],
                               'Status': app['status']}
    
print(app_df.head())
