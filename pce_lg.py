import requests,pce_ld,pce_auth,json,code,time
#code.interact(local=dict(globals(),**locals()))
#pce label group
def help():
    print('create_label_group() - > creates a label group with all labels from the same type')
    print('                         change variables in get_app_labels() to change label type')
    print('                         change "name" and "key" in create_post_data() to change name and label group type')

def login():
    global auth_creds, server,base_url_orgid,base_url
    auth_creds,base_url_orgid,base_url = pce_auth.connect()
    pce_ld.auth_creds = auth_creds
    pce_ld.base_url_orgid = base_url_orgid
    pce_ld.base_url = base_url


def login_error_handling():
    try: base_url
    except NameError:
        print('***************************************************************')
        print('Enter PCE login information before proceeding')
        print('***************************************************************')
        login()

        
def ll():
    load_login()


def load_login():
    pce_auth.load_host()



def get_app_labels():
    labels = pce_ld.get_labels()
    app_labels = []
    for i in labels:
        if i['key'] == 'app':
            app_labels.append(i['href'])
    return(app_labels)


def create_post_data():
    label_hrefs = get_app_labels()
    label_dict = []
    for labels in label_hrefs:
        label_dict.append({'href':labels})
    lg = {'name':'label-group-4','key':'app','labels':label_dict,'sub_groups': []}
    return(lg)


def create_label_group():
    a = auth_creds
    h = headers = {'Content-type':'application/json'}
    d = json.dumps(create_post_data())
    u = base_url_orgid + '/sec_policy/draft/label_groups'
    r = requests.post(u,data=d,auth=a,headers=h,verify=False)
    return(r)
    
    
    
        
    
