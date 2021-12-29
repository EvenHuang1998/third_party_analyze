#coding: utf-8

from collections import defaultdict
from time import sleep
import sys
import json
import dns.resolver

sys.path.append("D:\myfiles\code\\third_party_depen_analyze_final")
sys.path.append("../")
from utils import base_function

DIRECT_W_CDN_PATH="../data/direct_cdn/all_cdn_data.txt"
CDN_NS_ENTITY_RESULT_PATH="../result/indirect_cdn_ns/cdn_ns_entity.txt"
INDIRECT_W_NS_PATH="../result/indirect_cdn_ns/indirect_w_ns.txt"
INDIRECT_NS_PROVIDER_DOMAINS="../result/indirect_cdn_ns/indirect_ns_provider_domains.txt"
INDIRECT_NS_THIRD_RESULT = "../result/indirect_cdn_ns/indirect_ns_provider_third.txt"
INDIRECT_NS_CRITICAL_RESULT = "../result/indirect_cdn_ns/indirect_ns_provider_critical.txt"
INDIRECT_NS_NAME_THIRD_RESULT = "../result/indirect_cdn_ns/indirect_ns_name_third.txt"
INDIRECT_NS_NAME_CRITICAL_RESULT = "../result/indirect_cdn_ns/indirect_ns_name_critical.txt"


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
        answer = dns.resolver.resolve(domain, "NS")
    except:
        answer = ""
    ns_list = list()
    for ns in answer:
        ns = str(ns).strip(".")
        ns_list.append(ns)
    return ns_list

def get_ns_entity(ns_list):
    """
    Args:
        ns_list: A list of NSes.
    Returns:
        A dict of NS entity of all domain. This function also dumps the data info a file.
    """
    divider = base_function.NsDivider(ns_list)
    divider.divide()
    return divider.ns_entity

def get_ns_entity_of_cdnProvider():
    cdn_map=base_function.read_cdn_map()
    cdn_ns_entities_result=defaultdict(list)
    for cdn,cname_list in cdn_map.items():
        print(cdn)
        ns_set=set()
        for cname in cname_list:
            cname_tld=base_function.extract_tld(cname)
            ns_list=get_ns(cname_tld)
            ns_set=ns_set.union(ns_list)
        ns_entity_set=get_ns_entity(list(ns_set))
        cdn_ns_entities_result[cdn]=list(ns_entity_set)
        sleep(3)
    with open(CDN_NS_ENTITY_RESULT_PATH,"w") as f:
        json.dump(cdn_ns_entities_result,f,indent=2)
    return cdn_ns_entities_result

def get_indirect_w_cdn_ns_depen(cdn_ns_entity):
    result=dict()
    with open(DIRECT_W_CDN_PATH,"r") as f:
        direct_w_cdn=json.load(f)
    for w,cdn_info in direct_w_cdn.items():
        ns_set=set()
        cdn_list=cdn_info["cdn"]
        for cdn in cdn_list:
            ns_set=ns_set.union(cdn_ns_entity[cdn])
        result[w]=list(ns_set)
    with open(INDIRECT_W_NS_PATH,"w") as f:
        json.dump(result,f, indent=2)
    return result

def get_indirect_ns_provider_domains(indirect_w_ns_depen):
    result=defaultdict(list)
    for w,ns_entity_list in indirect_w_ns_depen.items():
        for ns_entity in ns_entity_list:
            # ns_entity_name=base_function.get_ns_entity_name(ns_entity)
            result[ns_entity].append(w)
    result=dict(sorted(result.items(),key=lambda kv:(len(kv[1]),kv[0]),reverse=True))
    with open(INDIRECT_NS_PROVIDER_DOMAINS,"w") as f:
        json.dump(result,f,indent=2)
    return result

def analyze_indirect_w_cdn_ns_third(indirect_w_ns_depen):
    result = defaultdict(dict)
    private_analyzer=base_function.PrivateAnalyzer()
    for domain,ns_list in indirect_w_ns_depen.items():
        for ns in ns_list:
            if ns not in result:
                result[ns]["third"] = set()
                result[ns]["private"] = set()
            
            if private_analyzer.is_other_private(ns,domain):
                result[ns]["private"].add(domain)
            else:
                result[ns]["third"].add(domain)
    for ns, depen_info in result.items():
        depen_info["third"] = list(depen_info["third"])
        depen_info["private"] = list(depen_info["private"])
        result[ns] = depen_info
    result = dict(sorted(result.items(), key=lambda kv: len(kv[1]["third"])+len(kv[1]["private"]),reverse=True))
    with open(INDIRECT_NS_THIRD_RESULT,"w") as f:
        json.dump(result,f,indent=2)
    return result

def analyze_indirect_w_cdn_ns_critical(indirect_w_ns_depen):
    result=defaultdict(dict)
    for w,ns_list in indirect_w_ns_depen.items():
        for ns in ns_list:
            if ns not in result:
                result[ns]["critical"] = set()
                result[ns]["noncritical"] = set()
            if len(ns_list)>1:
                result[ns]["noncritical"].add(w)
            else:
                result[ns]["critical"].add(w)
    for ns, depen_info in result.items():
        depen_info["critical"] = list(depen_info["critical"])
        depen_info["noncritical"] = list(depen_info["noncritical"])
        result[ns] = depen_info
    result = dict(sorted(result.items(), key=lambda kv: 
        len(kv[1]["critical"])+len(kv[1]["noncritical"]), reverse=True))
    with open(INDIRECT_NS_CRITICAL_RESULT,"w") as f:
        json.dump(result,f,indent=2)
    return result


def map_ns_entity_to_ns_name_third(source_data):
    result = defaultdict(dict)
    for ns_entity, domain_info in source_data.items():

        # ns_entity_name = base_function.whois_query(ns_entity)
        
        # if not ns_entity_name or ns_entity_name == "whois_error":
        #     ns_entity_name = base_function.extract_tld(ns_entity)
        ns_entity_name=base_function.get_ns_entity_name(ns_entity)
        print(ns_entity, ns_entity_name)
        if ns_entity_name not in result:
            result[ns_entity_name]["third"] = set()
            result[ns_entity_name]["private"] = set()
        result[ns_entity_name]["third"] = result[ns_entity_name]["third"].union(
            set(domain_info["third"]))
        result[ns_entity_name]["private"] = result[ns_entity_name]["private"].union(
            set(domain_info["private"]))
        sleep(2)
    for ns_entity_name, domain_info in result.items():
        domain_info["third"] = list(domain_info["third"])
        domain_info["private"] = list(domain_info["private"])
    with open(INDIRECT_NS_NAME_THIRD_RESULT, "w") as f:
        json.dump(result, f, indent=2)
    return result

def map_ns_entity_to_ns_name_critical(source_data):
    result=defaultdict(dict)
    for ns_entity, domain_info in source_data.items():
        ns_entity_name=base_function.get_ns_entity_name(ns_entity)
        print(ns_entity,ns_entity_name)
        if ns_entity_name not in result:
            result[ns_entity_name]["critical"]=set()
            result[ns_entity_name]["noncritical"]=set()
        result[ns_entity_name]["critical"] = result[ns_entity_name]["critical"].union(set(domain_info["critical"]))
        result[ns_entity_name]["noncritical"] = result[ns_entity_name]["critical"].union(
            set(domain_info["noncritical"]))
        sleep(2)
    for ns_entity_name,domain_info in result.items():
        domain_info["critical"]=list(domain_info["critical"])
        domain_info["noncritical"]=list(domain_info["noncritical"])
    with open(INDIRECT_NS_NAME_CRITICAL_RESULT, "w") as f:
        json.dump(result, f, indent=2)
    return result

def main():
    # print("-----Get NS entities of CDN Provider-----")
    # cdn_ns_entity=get_ns_entity_of_cdnProvider()
    with open(CDN_NS_ENTITY_RESULT_PATH,"r") as f:
        cdn_ns_entity=json.load(f)
    print("-----Get Indirect w-cdn-ns Dependency-----")
    indirect_w_ns_depen=get_indirect_w_cdn_ns_depen(cdn_ns_entity)
    print("-----Get Indirect NS Provider Domains-----")
    indirect_ns_domains=get_indirect_ns_provider_domains(indirect_w_ns_depen)
    print("-----Analyze Indirect NS Third-----")
    third=analyze_indirect_w_cdn_ns_third(indirect_w_ns_depen)
    print("-----Analyze Indirect NS Critical-----")
    critical=analyze_indirect_w_cdn_ns_critical(indirect_w_ns_depen)
    print("-----Map NS Entity to NS Entity Name")
    result_third=map_ns_entity_to_ns_name_third(third)
    result_critical=map_ns_entity_to_ns_name_critical(critical)
    print("-----Finish-----")


if __name__ == '__main__':
    main()
