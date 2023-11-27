import requests

#For the items below, replace with the info for the PCE you are connecting to.
#The info has to be within quotes
#########################################
server = 'pce-225.lab.com:8443'  #####Replace with your PCE address and port
api_user = 'api_10xxx0fd2ess06976'      #####Replace with your API user
api_key = '7814900d0asdff9fef7640fb82e9basdfadsfadsf87b663dc70086f6ff9168da4'  #####Replace with your API key
org_id = '1'  #####Replace with your org ID
#########################################



def connect():
    auth_creds = requests.auth.HTTPBasicAuth(api_user,api_key)
    base_url = f'https://{server}/api/v2'
    base_url_orgid = f'https://{server}/api/v2/orgs/{org_id}'
    return auth_creds,base_url_orgid,base_url
