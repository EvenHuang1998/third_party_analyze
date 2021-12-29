#coding: utf-8
from collections import defaultdict
from time import sleep
import sys
import json
import dns.resolver

sys.path.append("D:\myfiles\code\\third_party_depen_analyze_final")
sys.path.append("../")
from utils import base_function

DIRECT_W_CA_PATH="../data/direct_ca/all_ca_data.txt"
CA_NS_ENTITY_RESULT_PATH="../result/indirect_ca_ns/ca_ns_entity.txt"
INDIRECT_W_CA_NS_PATH="../result/indirect_ca_ns/indirect_w_ca_ns.txt"
INDIRECT_CA_PROVIDER_DOMAINS="../result/indirect_ca_ns/indirect_ns_provider_domains.txt"
INDIRECT_NS_THIRD_RESULT="../result/indirect_ca_ns/indirect_ns_provider_third.txt"
INDIRECT_NS_CRITICAL_RESULT = "../result/indirect_ca_ns/indirect_ns_provider_critical.txt"
INDIRECT_NS_NAME_THIRD_RESULT = "../result/indirect_ca_ns/indirect_ns_name_third.txt"
INDIRECT_NS_NAME_CRITICAL_RESULT = "../result/indirect_ca_ns/indirect_ns_name_critical.txt"

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

def get_ns_entity_of_caProvider():
    ca_url_dict=defaultdict(set)
    ca_ns_set=defaultdict(set)
    ca_ns_entities_result = dict()
    with open(DIRECT_W_CA_PATH,"r") as f:
        ca_data=json.load(f)

    #首先统计所有出现过的CA用到的CA URL
    for domain,ca_info in ca_data.items():
        if "issuer" in ca_info and "organizationName" in ca_info["issuer"]:
           issuer=ca_info["issuer"]["organizationName"]
        else:
            continue
        if ("ca_url" not in ca_info) or (not ca_info["ca_url"]):
            continue
        else:
            ca_url=ca_info["ca_url"][0]
        ca_url_dict[issuer].add(ca_url)
    #然后用这些CA URL得到它所用的NS，并由NS得到NS Entity
    for issuer,ca_url_set in ca_url_dict.items():
        for ca_url in ca_url_set:
            tld_ca_url=base_function.extract_tld(ca_url)
            ns_list=get_ns(tld_ca_url)
            ca_ns_set[issuer]=ca_ns_set[issuer].union(set(ns_list))
        ns_entity_set= get_ns_entity(list(ca_ns_set[issuer]))#base_function.map(list(ca_ns_set[issuer]))
        ca_ns_entities_result[issuer]=list(ns_entity_set)
    with open(CA_NS_ENTITY_RESULT_PATH,"w") as f:
        json.dump(ca_ns_entities_result,f,indent=2)
    return ca_ns_entities_result


def get_indirect_w_ca_ns_depen(ca_ns_entity):
    result = dict()
    with open(DIRECT_W_CA_PATH, "r") as f:
        direct_w_ca = json.load(f)
    for w, ca_info in direct_w_ca.items():
        if "issuer" in ca_info and "organizationName" in ca_info["issuer"]:
            issuer=ca_info["issuer"]["organizationName"]
        else:
            continue
        result[w] = ca_ns_entity[issuer]
    with open(INDIRECT_W_CA_NS_PATH, "w") as f:
        json.dump(result, f, indent=2)
    return result


def get_indirect_ns_provider_domains(indirect_w_ns_depen):
    result = defaultdict(list)
    for w, ns_entity_list in indirect_w_ns_depen.items():
        for ns_entity in ns_entity_list:
            result[ns_entity].append(w)
    result = dict(sorted(result.items(), key=lambda kv: (
        len(kv[1]), kv[0]), reverse=True))
    with open(INDIRECT_CA_PROVIDER_DOMAINS, "w") as f:
        json.dump(result, f, indent=2)
    return result


def analyze_indirect_w_cdn_ns_third(indirect_w_ns_depen):
    result = defaultdict(dict)
    private_analyzer = base_function.PrivateAnalyzer()
    for domain, ns_list in indirect_w_ns_depen.items():
        for ns in ns_list:
            if ns not in result:
                result[ns]["third"] = set()
                result[ns]["private"] = set()

            if private_analyzer.is_other_private(ns, domain):
                result[ns]["private"].add(domain)
            else:
                result[ns]["third"].add(domain)
    for ns, depen_info in result.items():
        depen_info["third"] = list(depen_info["third"])
        depen_info["private"] = list(depen_info["private"])
        result[ns] = depen_info
    result = dict(sorted(result.items(), key=lambda kv: 
                        len(kv[1]["third"])+len(kv[1]["private"]), reverse=True))
    with open(INDIRECT_NS_THIRD_RESULT, "w") as f:
        json.dump(result, f, indent=2)
    return result


def analyze_indirect_w_cdn_ns_critical(indirect_ns_domains,indirect_w_ns_depen):
    result = defaultdict(dict)
    for ns, domain_list in indirect_ns_domains.items():
        if ns not in result:
            result[ns]["critical"] = set()
            result[ns]["noncritical"] = set()
        for domain in domain_list:
            if len(indirect_w_ns_depen[domain])>1:
                result[ns]["noncritical"].add(domain)
            else:
                result[ns]["critical"].add(domain)
        # if len(w_list) > 1:
        #     result[ns]["noncritical"]=result[ns]["noncritical"].union(set(w_list))
        # else:
        #     result[ns]["critical"] = result[ns]["critical"].union(
        #         set(w_list))
    for ns, depen_info in result.items():
        depen_info["critical"] = list(depen_info["critical"])
        depen_info["noncritical"] = list(depen_info["noncritical"])
        result[ns] = depen_info
    result = dict(sorted(result.items(), key=lambda kv:
                         len(kv[1]["critical"])+len(kv[1]["noncritical"]), reverse=True))
    with open(INDIRECT_NS_CRITICAL_RESULT, "w") as f:
        json.dump(result, f, indent=2)
    return result


def map_ns_entity_to_ns_name_third(source_data):
    result = defaultdict(dict)
    for ns_entity, domain_info in source_data.items():
        ns_entity_name = base_function.whois_query(ns_entity)
        if not ns_entity_name or ns_entity_name == "whois_error":
            # if "awsdns-" in ns_entity:
            #     ns_entity_name="AMAZON"
            # elif "azure" in ns_entity:
            #     ns_entity_name="MICROSOFT AZURE"
            # elif "akam.net" in ns_entity:
            #     ns_entity_name="AKAMAI"
            # elif "apple.com" in ns_entity:
            #     ns_entity_name="APPLE"
            # elif "dynect" in ns_entity:
            #     ns_entity_name="DYNECT"
            # elif "cloudflare" in ns_entity:
            #     ns_entity_name="CLOUDFLARE"
            ns_entity_name=base_function.extract_tld(ns_entity)
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
    result = defaultdict(dict)
    for ns_entity, domain_info in source_data.items():
        ns_entity_name = base_function.whois_query(ns_entity)
        
        if not ns_entity_name or ns_entity_name == "whois_error" or "PRIVACY" in ns_entity_name \
             or "REDACTED" in ns_entity_name or "PROTECTION" in ns_entity_name:
            ns_entity_name=base_function.extract_tld(ns_entity)
        print(ns_entity, ns_entity_name)
        if ns_entity_name not in result:
            result[ns_entity_name]["critical"] = set()
            result[ns_entity_name]["noncritical"] = set()
        result[ns_entity_name]["critical"] = result[ns_entity_name]["critical"].union(
            set(domain_info["critical"]))
        result[ns_entity_name]["noncritical"] = result[ns_entity_name]["noncritical"].union(
            set(domain_info["noncritical"]))
        sleep(2)
    for ns_entity_name, domain_info in result.items():
        domain_info["critical"] = list(domain_info["critical"])
        domain_info["noncritical"] = list(domain_info["noncritical"])
    with open(INDIRECT_NS_NAME_CRITICAL_RESULT, "w") as f:
        json.dump(result, f, indent=2)
    return result


def main():
    print("-----Get NS Entity of CA Provider-----")
    ca_ns_entity=get_ns_entity_of_caProvider()
    print("-----Get Indirect w-ca-ns Dependency-----")
    indirect_w_ns_depen = get_indirect_w_ca_ns_depen(ca_ns_entity)
    print("-----Get Indirect NS Provider Domains-----")
    indirect_ns_domains = get_indirect_ns_provider_domains(indirect_w_ns_depen)
    print("-----Analyze Indirect NS Third-----")
    third = analyze_indirect_w_cdn_ns_third(indirect_w_ns_depen)
    print("-----Analyze Indirect NS Critical-----")
    critical = analyze_indirect_w_cdn_ns_critical(indirect_ns_domains,indirect_w_ns_depen)
    print("-----Map NS Entity to NS Entity Name")
    result_third = map_ns_entity_to_ns_name_third(third)
    result_critical = map_ns_entity_to_ns_name_critical(critical)
    print("-----Finish-----")

if __name__ == '__main__':
    main()
