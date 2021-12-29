#coding: utf-8

import sys
import json
import dns.resolver
from collections import defaultdict
from time import sleep

sys.path.append("D:\myfiles\code\\third_party_depen_analyze_final")
sys.path.append("../")
from utils import base_function


DEST_FILEPATH="../data/direct_ns/"


def get_ns(domain):
    """
    Args: 
        domain: str, domain that needs to query NS.
    
    Returns:
        A list cotains NSes of the domain. The last dot of NS domain will be removed.
        If something wrong happened, a null list will be returned.
        
        example:
        ["ns7.baidu.com","dns.baidu.com","ns4.baidu.com"] 
        
    """
    
    try:
        answer=dns.resolver.resolve(domain,"NS")
    except:
        answer=""
    ns_list=list()
    for ns in answer:
        ns=str(ns).strip(".")
        ns_list.append(ns)
    return ns_list

def get_all_ns(rank_data):
    """
    Args:
        rank_data: dict of original rank data.
    
    Returns:
        A dict of NSes of all domain. This function also store the NS data to a file.
        If a domain doesn't have NSes, it will be dismissed.

        example:
        {
            "google.com":["ns1.google.com","ns2.google.com"]
        }
    """

    all_ns=defaultdict(dict)
    for rank,domain in rank_data.items():
        print(rank,domain)
        ns_list=get_ns(domain)
        if not ns_list:  #对于没有ns的域名，不考虑
            continue
        all_ns[domain]["rank"]=rank
        all_ns[domain]["ns_list"]=ns_list
        sleep(1)
        
    filename=DEST_FILEPATH+"ns.txt"
    with open(filename,"w") as f:
        json.dump(all_ns,f,indent=2)
    return all_ns

def get_ns_entity(all_ns,result):
    """
    Args:
        all_ns: dict of all ns info.
    Returns:
        A dict of NS entity of all domain. This function also dumps the data info a file.
    """
    for domain, ns_info in all_ns.items():
        rank=ns_info["rank"]
        print(domain)
        ns_list=ns_info["ns_list"]
        divider = base_function.NsDivider(ns_list)
        divider.divide()
        result[domain]["rank"]=ns_info["rank"]
        result[domain]["ns_entity"]=list(divider.ns_entity)
    filename=DEST_FILEPATH+"ns_entity.txt"
    with open(filename,"w") as f:
        json.dump(result,f,indent=2)
    return result


def get_ns_entity_name(result):
    """
    Args:
        all_ns_entity: dict of ns entity of all domain
    Returns:
        A dict of ns entity and ns entity name of all domain.
        example:
        {
            "qq.com":["Tencent"],
            "baidu.com":["Baidu"]
        } 
    """
    for domain,ns_info in result.items():
        rank=ns_info["rank"]
        entity_name_set=set()
        for entity in ns_info["ns_entity"]:
            # org=base_function.whois_query(entity)
            # if not org or org=="whois_error":
            #     continue
                #org=base_function.extract_tld(ns_entity)
            org=base_function.get_ns_entity_name(entity)
            print(rank,domain,org)
            entity_name_set.add(org)
            sleep(2)
        result[domain]["ns_entity_name"]=list(entity_name_set)
    filename=DEST_FILEPATH+"ns_entity_name.txt"
    with open(filename,"w") as f:
        json.dump(result,f,indent=2)
    return result

def analyze_ns_private(result):
    private_analyzer=base_function.PrivateAnalyzer()
    for domain,ns_info in result.items():
        print(domain)
        third=list()
        private=list()
        for ns_entity in ns_info["ns_entity"]:
            if private_analyzer.is_other_private(domain,ns_entity):
                private.append(ns_entity)
            else:
                third.append(ns_entity)
        result[domain]["third"]=third
        result[domain]["private"]=private
    return result

def analyze_ns_critical(result):
    """
    如果只用了一个第三方的NS，则认为对这个第三方的NS critical
    """
    for domain,ns_info in result.items():
        print(domain)
        if not ns_info["private"] and len(ns_info["third"])<2:
            result[domain]["critical"]=True
        else:
            result[domain]["critical"]=False
    return result


def main():
    result=defaultdict(dict)
    print("-----loading rank data-----")
    rank_data = base_function.load_rank_data()
    print("-----get all ns-----")
    all_ns = get_all_ns(rank_data)
   
    print("-----get all ns entity-----")
    result=get_ns_entity(all_ns,result)

    print("-----get all ns entity name-----")
    result=get_ns_entity_name(result)
    print("-----analyze ns private-----")
    result=analyze_ns_private(result)
    print("-----analyze ns critical-----")
    result=analyze_ns_critical(result)
    print("-----store ns data-----")
    filename=DEST_FILEPATH+"all_ns_data_new.txt"
    with open(filename,"w") as f:
        json.dump(result,f,indent=2)
    print("-----finish ns-----")

if __name__ == "__main__":
    main()
