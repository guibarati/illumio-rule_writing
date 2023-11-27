import requests,json,code,getpass
requests.packages.urllib3.disable_warnings()

host = ''

def help():
    print('save() -> saves the login information to json file, except password')
    print('load_host() -> loads login information from saved json file, except password')
    print('connect() -> collects connection and login information and calls the login function')
    print('login(username,password,server,saas) -> receives connection and login information and create session login')


def save():
    data = {}
    data['username'] = username
    data['server'] = server
    data['saas'] = saas
    with open('login_info.json','w') as f:
        json.dump(data, f)

def load_host():
    global host
    host = {}
    with open('login_info.json','r') as f:
        host = json.load(f)

    

def connect():
    global host,auth_creds, server,base_url_orgid,base_url,username,saas
    if host != '':
        print('Login from loaded information')
        print('Username: ' + host['username'])
        print('PCE Host: ' + host['server'])
        password =  getpass.getpass('Password : ')
        username = host['username']
        server = host['server']
        saas = host['saas']
    if host == '':
        username = input('Username : ')
        password = getpass.getpass('Password : ')
        server =  input('Server fqdn:port : ')
        saas = 'a'
    while saas.lower() not in ['y','n']:
        saas = input('SaaS PCE - Y/N :')
    if saas.lower() == 'y':
        l = login(username,password,server,saas)
    else:
        l = login(username,password,server)
    if 'NoneType' not in str(type(l)):
        auth_creds = requests.auth.HTTPBasicAuth(l['auth_username'],l['session_token'])
        base_url_orgid = 'https://' + server + '/api/v2/orgs/' + str(l['org_id'])
        base_url = 'https://' + server + '/api/v2'
        return(auth_creds,base_url_orgid,base_url)

def login(username,password,server,saas='n'):
    if saas.lower()=='n':
        url_auth = 'https://' + server + '/api/v2/login_users/authenticate?pce_fqdn=' + server.split(':')[0]
    if saas.lower() == 'y':
        url_auth = 'https://login.illum.io:443/api/v2/login_users/authenticate?pce_fqdn=' + server.split(':')[0]
    headers = {'Content-Type' : 'application/json'}
    try:
        r = requests.post(url_auth,headers=headers, auth=requests.auth.HTTPBasicAuth(username,password), verify=False)
    except Exception as e:
        print(e)
        print('\nCheck if PCE FQDN and Port are correct and accessible')
        return
    if r.status_code in [200,201,202]:
        js = json.loads(r.text)
        auth_token = js['auth_token']
        url_login = 'https://' + server + '/api/v2/users/login'
        headers['Authorization'] = 'Token token=' + auth_token
        r = requests.get(url_login,headers=headers,verify=False)
        js = json.loads(r.text)
        #code.interact(local=dict(globals(),**locals()))
        if 'org_id' in js:
            session_token = {'auth_username':js['auth_username'],'session_token' : js['session_token'],'org_id':js['org_id']}
        else:
            session_token = {'auth_username':js['auth_username'],'session_token' : js['session_token'],'org_id':js['orgs'][0]['org_id']}
        return(session_token)
    if r.status_code == 401:
        print('\nInvalid Credentials')
    else:
        print(r.text)
    
