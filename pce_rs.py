#pce Rule Set Script 
import requests,pce_ld,pce_auth,openpyxl,os,code,json,pce_fs,pce_lf
#code.interact(local=dict(globals(),**locals()))


def help():
    print('apply_rules() -> - logs in to PCE')
    print('                 - compile rules from excel file')
    print('                 - convert port/protocol to existing services')
    print('                 - create new rules on selected ruleset')
    print('save_login() -> - Saves the login information, except password')
    print('save_file_info() -> - Saves Excel file name and location path. Except sheet name')
    print('ll() -> - Load login information, except password')
    print('lf() -> - Loads Excel file name and location path. Except sheet name')
    

def login_error_handling():
    try: base_url
    except NameError:
        print('***************************************************************')
        print('Enter PCE login information before proceeding')
        print('***************************************************************')
        login()


def save_login():
    pce_auth.save()


def ll():
    load_login()


def lf():
    load_file_info()


def load_login():
    pce_auth.load_host()


def save_file_info():
    pce_lf.save()


def load_file_info():
    pce_lf.load_file_info()


def login():
    global auth_creds, server,base_url_orgid,base_url
    auth_creds,base_url_orgid,base_url = pce_auth.connect()
    pce_ld.auth_creds = auth_creds
    pce_ld.base_url_orgid = base_url_orgid
    pce_ld.base_url = base_url



def build_data():
    rule_list = pce_lf.merge_lines()
    rulepost = []
    for i in rule_list:
        rule = {}
        rule['providers'] = []
        rule['consumers'] = []
        rule['ingress_services'] = []
        for j in i:
            if 'Provider' in j:
                for k in i[j]:
                    rule['providers'].append(k)                
            if 'Consumer' in j:
                for k in i[j]:
                    rule['consumers'].append(k)
            if 'Port' in j:
                for k in i[j]:
                    rule['ingress_services'].append(k)
        rulepost.append(rule)
    return(rulepost)


def scope_decision():
    print('place holder')
    

def put_data():
    global label_and_iplist_index
    try:
        label_and_iplist_index = pce_ld.labels_and_iplists()
        lines = build_data()
        rules = []
        for i in lines:
            consumers = []
            providers  =[]
            ingress_services = []
            for j in i['consumers']:
                if '(blank)' not in j:
                    ip = j.split(';')[0]
                    ic = label_and_iplist_index[ip]
                    if '/labels/' in ic:
                        consumers.append({'label':{'href':ic}})
                    if '/ip_lists/' in ic:
                        consumers.append({'ip_list':{'href':ic}})
                    #consumers.append({'label':{'href':label_index[j]}})
            for j in i['providers']:
                if '(blank)' not in j:
                    ip = j.split(';')[0]
                    ic = label_and_iplist_index[ip]
                    if '/labels/' in ic:
                        providers.append({'label':{'href':ic}})
                    if '/ip_lists/' in ic:
                        providers.append({'ip_list':{'href':ic}})
            if len(providers) == 0:
                providers.append({"actors": "ams"})
                    #providers.append({'label':{'href':label_index[j]}})
            for j in i['ingress_services']:
                ingress_services.append(j)
            rules.append({'consumers':consumers,'providers':providers,'ingress_services':ingress_services})
        for i in rules:
            i['unscoped_consumers'] = True
            i['enabled'] = True
            i['resolve_labels_as'] = {'providers':['workloads'],'consumers':['workloads']}
            for j in i['ingress_services']:
                if j['proto'] == 'TCP':
                    j['proto'] = 6
                if j['proto'] == 'UDP':
                    j['proto'] = 17
        rules_and_services = pce_fs.update_services(rules)
        return(rules_and_services)
    except KeyError as e:
        print('Error! - Excel File contain label not present on PCE - ' + str(e))
  


def select_ruleset():
    global label_and_iplist_index
    label_and_iplist_index = pce_ld.labels_and_iplists()
    ruleset_index,ruleset_list = pce_ld.rulesets()
    filtered_list = []
    filter_name = input('Display rulesets matching the text: ')
    filter_name = filter_name.lower()
    for i in ruleset_list:
        rule_name = i['name'].lower()
        if filter_name in rule_name:
            filtered_list.append(i)
    selection = []
    for i in filtered_list:
        selection.append(i['name'])
        print(selection.index(i['name']),' Ruleset Name: ',i['name'])
        for j in i['scopes'][0]:
            print('       Scope: ',label_and_iplist_index[j['label']['href']])
        print('')
    rs_select = ''
    while rs_select not in ruleset_index:
        r = input('Enter the Ruleset number where the rules will be applied: ')
        if int(r) < len(selection):
            rs_select = selection[int(r)]
    return(ruleset_index[rs_select])
                

def apply_rules():
    login_error_handling()
    global base_url,auth_creds
    api_url = base_url + select_ruleset()+ '/sec_rules'
    headers = {'Content-type':'application/json'}
    new_rules = put_data()
    for i in new_rules:
        post_data = json.dumps(i)
        r = requests.post(api_url,data=post_data,auth=auth_creds,headers=headers,verify=False)
        if r.status_code not in [200,201,202,203,204]:
            print(post_data)
            print(r.text)
            print('')
