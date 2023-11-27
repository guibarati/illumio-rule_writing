import time,json,requests,code
#code.interact(local=dict(globals(),**locals()))

def help():
    print('getdata() -> Sends an asynchronous request to PCE and fetches result')

def getdata(api_url,auth_creds,base_url):
    headers = {'Accept': 'application/json','Prefer':'respond-async'}
    r = requests.get(api_url,headers=headers,auth=auth_creds,verify=False)
    print('waiting for the PCE to process the request')
    req_job = r.headers
    if '202' in req_job['Status']:
        wait_time = int(req_job['Retry-After'])
        time.sleep(wait_time)
        api_url = base_url + req_job['Location']
        headers = {'Accept':'application/json'}
        r = requests.get(api_url,headers=headers,auth=auth_creds,verify=False)
        job_status = json.loads(r.text)
        retry = 1
        while job_status['status'] != 'done' and retry < 4:
            print('Retrying in ' + str(wait_time) + ' seconds.')
            time.sleep(wait_time)
            r = requests.get(api_url,headers=headers,auth=auth_creds,verify=False)
            job_status = json.loads(r.text)
            retry += 1
        if retry >= 4:
            print(' ')
            print(' ')
            print('Request timeout')
            print(' ')
            print(' ')
        else:
            url_result = job_status['result']['href']
            api_url = base_url + url_result
            r = requests.get(api_url,headers=headers,auth=auth_creds,verify=False)
            result = json.loads(r.text)
            return(result)
            
    
    
    
