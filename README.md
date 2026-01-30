# DataHubTools
## Various scripts that I use for DH tasks

### CDECurrencyCheck.py
Reads and MDF model and determines if any of hte CDEs have been retired and if so, what is the new version.  Marginally useful in an MDB world

### CRDC_CDE.ipynb
A Jupyter notebook that gets all CRDC CDEs and their PVs.  Marginally useful at best.

### FileIDinator.py
Adds a CRDC friendly file identifier to a file manifest.  Useful.

### KFIDandConsentCheck.py
So Kids First has a problem.  The IDs they gave GC and the IDs in dbGaP don't match.  They're trying to update dbGaP, but it's slow going.  So this script takes a CCDI provided KF-dbGaP mapping file and checks that the GC IDs are mapped to a valid dbGaP ID and consent code.

Requires a configuration file, see *kf_dbgap_config.yml* for an example.

**Runtime options**
-c/--configfile : Full path to the configuration file

-v/--verbose :  Verbose output.  Adding more "v"'s gets more verbose.  Example -vv, -vvv

**Configuration File options**
Note that the configuration file must be in YAML format\
- **phs**: The dbGaP phs number for the project\
- **mapping_file**: The full path to the file containin the mapping betweek the KF Ids and the dbGaP IDs.\
- **submitted_file**: The GC Participant node submission file.  Can be obtained from the data view in the submission.\
- **consent_file**: The GC Consent node submission file.  Also can be obtained from the data view in the submission.\
- **report_file**: The full path for the file where the report on matching will be saved.\
- **dbgapinfo_file**: The full path for the file where the output of an SSTR query for the phs number will be saved.  Use None if the output should not be saved.\
- **sstrfile**: The full path to the file saved by the dbgapinfo_file.  If present, the script will use this file instead of the dbGaP API.  Recommended, the API is slower and dbGaP gets grumpy if you hit the API too much.  Use None to use the API.\
- **testrun**: True/False.  USE FOR DEVELOPMENT/TESTING ONLY, this limits the number of queries to the SSTR API.  


### MDFCDEVersionator.py
This was done to help ICDC, it reads in an MDF file and adds version numbers to any CDE entry missing the version number.  While potentially useful, it needs a re-write now that bento_mdf supports model writing.

### PVCountenator.py
Creates a report on which CDEs in a model have PVs and which do not.  Potentially still useful.

### RandomFileGenerator.py
Creates files containing random text or random binary.  Used in creating fake files for DH file upload demos.

### RequiredNodesTest.py
Reads an MDF and spits out lists of required and optional nodes.  Does use bento_mdf so it may be marginally useful for reporting purposes

### SSTR_Check.py
An early version of what becam KFIDandConsentCheck.py.  Needs work but useful as an example.

### SubmissionFixmogrifier
This script was written to fix common mistakes in DH submissions and populate the key fields.  Is largely OBE since DH now does key fields for submitters.

### SubmissionRequetinator.py
And attempt to use the submission request API to generate a report on submission requests in the system.  May have uses.


