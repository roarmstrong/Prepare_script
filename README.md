# Prepare_script
Prepare script for Sentinel 2 COG data
# Usage of script 
- ` python ls_s2_cog.py <bucket_name>`
- Make sure datacube.conf is in the Home directory
- If passing a different config file then the usage is :
- `python la_s2_cog.py -c <config_file> <bucket_name> <--prefix>`
    - bucket_name = S3 bucket name to access
    - --prefix = start of Object_key

