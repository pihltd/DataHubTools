# DataHubTools
## Various scripts that I use for DH tasks

### CDECurrencyCheck.py
Reads and MDF model and determines if any of hte CDEs have been retired and if so, what is the new version.  Marginally useful in an MDB world

### CRDC_CDE.ipynb
A Jupyter notebook that gets all CRDC CDEs and their PVs.  Marginally useful at best.

### FileIDinator.py
Adds a CRDC friendly file identifier to a file manifest.  Useful.

### KFIDandConsentCheck.py
So Kids First has a problem.  The IDs they gave GC and the IDs in dbGaP don't match.  They're trying to update dbGaP, but it's slow going.  So this script takes a CCDI provided KF-dbGaP mapping file and checks that the GC IDs are mapped to a valid dbGaP ID and consent code. \
Requires a configuration file, see *kf_dbgap_config.yml* for an example. \

**Runtime options**
-c/--configfile : Full path to the configuration file
-v/--verbose :  Verbose output.  Adding more "v"'s gets more verbose.  Example -vv, -vvv


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


