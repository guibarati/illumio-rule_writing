import json,code,pce_ld
#code.interact(local=dict(globals(),**locals()))

def help():
    print('classify_services() -> assign each service object a score based on total number of matching ports')
    print('find_services(rules) -> receives the rules to be applied and compares the port and protocol with existing service objects')
    print('                        Services with the lowest score (covering the least ports/more specicific) are selected')
    print('update_services(rules) -> Removes the explicit port and protocol configuration and adds service object to the rules')


    
def classify_services():
    global si,sp
    si,sp = pce_ld.services()
    ss = {}
    for k,v in sp.items():
        items_score = 0
        for i in v:
            if 'to_port' in i:
                item_score = int(i['to_port']) - int(i['port'])
            else:
                item_score = 0
            items_score = items_score + item_score
        sts = items_score + len(v)
        ss[k] = sts
    return(si,sp,ss)


def find_services(rules):
    si,sp,ss = classify_services()
    max_port_range = 20
    for i in rules:
        for j in i['ingress_services']:
            is_port = j['port']
            is_proto = j['proto']
            for k,v in sp.items():
                for l in v:
                    if 'port' in l:
                        s_port = l['port']
                        s_proto = l['proto']
                        s_score = ss[k]
                        if is_port == s_port and is_proto == s_proto and 'to_port' not in l:
                            if 'candidate_service' in j:
                                if s_score < ss[j['candidate_service']]:
                                                j['candidate_service'] = k
                            else:
                                j['candidate_service'] = k

                        if 'to_port' in l:
                            s_toport = l['to_port']
                            if is_port >= s_port and is_port <= s_toport and is_proto == s_proto:
                                if s_score < 20 or k == 'S-HIGH-TCP-PORTS':
                                    
                                    if 'candidate_service' in j:
                                        if s_score < ss[j['candidate_service']]:
                                                j['candidate_service'] = k
                                    else:
                                        j['candidate_service'] = k
    return(rules)


def update_services(rules):
    global si
    find_services(rules)
    print('')
    print('{:<8} {:<8} {}'.format('Port','Protocol','Service'))
    for i in rules:
        for j in i['ingress_services']:
            if 'candidate_service' in j:
                if j['proto'] == 6:
                    proto = 'TCP'
                if j['proto'] == 17:
                    proto = 'UDP'
                #print(j['port'],' ',proto,' service-> ',j['candidate_service'])
                print('{:<8} {:<8} {}'.format(j['port'],proto,j['candidate_service']))
        a = 'a'
    while a.lower() not in ['y','n']:
        print('')
        a = input('Replace Port and Protocol with Service? (y/n): ')
        
    if a.lower() == 'y':
        for i in rules:
            new_services = []
            for j in i['ingress_services']:
                if 'candidate_service' in j:
                    if {'href':si[j['candidate_service']]} not in new_services:
                        new_services.append({'href':si[j['candidate_service']]})
                else:
                    new_services.append(j)
                i['ingress_services'] = new_services
    else:
        for i in rules:
            for j in i['ingress_services']:
                j.pop('candidate_service',None)
    return(rules)
                        
                
