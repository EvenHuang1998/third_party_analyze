from collections import defaultdict
import json
import tldextract
import sys
import dns.resolver

sys.path.append("D:\myfiles\code\\third_party_depen_analyze_final")
sys.path.append("../")

from utils import base_function

DIRECT_W_CA_PATH="../data/direct_ca/all_ca_data.txt"
CA_CDN_RESULT_PATH="../result/indirect_ca_cdn/ca_cdn_.txt"
INDIRECT_W_CDN_PATH="../result/indirect_ca_cdn/indirect_w_cdn.txt"
INDIRECT_CDN_PROVIDER_DOMAINS="../result/indirect_ca_cdn/indirect_cdn_provider_domains.txt"
INDIRECT_CDN_THIRD_RESULT="../result/indirect_ca_cdn/indirect_cdn_third.txt"
INDIRECT_CDN_CRITICAL_RESULT = "../result/indirect_ca_cdn/indirect_cdn_critical.txt"

class CdnExtractor(object):
    def __init__(self):
        self.cdn_map_dict = None

    def recursively_get_cname(self, link):
        ext = tldextract.extract(link)
        pre_cname = ext.subdomain+'.'+ext.registered_domain
        cnames = []
        while True:
            try:
                answer = dns.resolver.resolve(pre_cname, "CNAME")
                cname = str(answer[0])
                if pre_cname == cname:
                    break
                else:
                    cnames.append(cname)
                    pre_cname = cname
            except:
                break
        return cnames

    def map_cname_list_to_cdn(self, cname_list):
        cdn_list = []
        for cname in cname_list:
            cname_tld = base_function.extract_tld(cname)
            for cdn, cnames in self.cdn_map_dict.items():
                if cname_tld in cnames:
                    cdn_list.append(cdn)
        return cdn_list

    def initialize(self):
        self.cdn_map_dict = base_function.read_cdn_map()

def get_ca_url_dict(direct_ca_data):
    ca_url_dict=defaultdict(list)
    for domain,ca_info in direct_ca_data.items():
        if ("ca_url" not in ca_info) or (not ca_info["ca_url"]):
            continue
        if "issuer" not in direct_ca_data[domain] \
                or "organizationName" not in direct_ca_data[domain]["issuer"]:
            continue
        ca_issuer=ca_info["issuer"]["organizationName"]

        ca_url=ca_info["ca_url"][0]
        ca_url_dict[ca_issuer].append(ca_url)
    for ca,ca_url_set in ca_url_dict.items():
        ca_url_dict[ca]=list(set(ca_url_set))
    return ca_url_dict

def get_cdn_of_caProvider(ca_url_dict):
    cdn_extractor=CdnExtractor()
    cdn_extractor.initialize()

    ca_cdn_dict=defaultdict(dict)
    for ca,ca_url_list in ca_url_dict.items():
        print(ca)
        cname_set = set()
        for ca_url in ca_url_list:
            cname_list = cdn_extractor.recursively_get_cname(ca_url)
            cname_set = cname_set.union(cname_list)
        cdn_list = cdn_extractor.map_cname_list_to_cdn(list(cname_set))
        cdn_set = set(cdn_list)
        if cdn_set:
            ca_cdn_dict[ca]["cdn"] = list(cdn_set)
            ca_cdn_dict[ca]["cname"] = list(cname_set)
    with open(CA_CDN_RESULT_PATH,"w") as f:
        json.dump(ca_cdn_dict,f,indent=2)
    return ca_cdn_dict


def get_indirect_w_ca_cdn_depen(ca_cdn):
    result = dict()
    with open(DIRECT_W_CA_PATH, "r") as f:
        direct_w_ca = json.load(f)
    for w, ca_info in direct_w_ca.items():
        if "issuer" not in ca_info \
                or "organizationName" not in ca_info["issuer"]:
            continue
        issuer = ca_info["issuer"]["organizationName"] #得到w用的ca:一个w只会有一个ca
        if issuer not in ca_cdn:
            continue
        result[w]=ca_cdn[issuer]["cdn"]  #得到ca用的cdn和cname, 这一个ca用的cdn和cname就是
                                                #这个w依赖的cdn和cname

    with open(INDIRECT_W_CDN_PATH, "w") as f:
        json.dump(result, f, indent=2)
    return result

def get_indirect_cdn_provider_domains(indirect_w_cdn_depen):
    result = defaultdict(list)
    for w, cdn_list in indirect_w_cdn_depen.items():
        for cdn in cdn_list:
            result[cdn].append(w)
    result = dict(sorted(result.items(), key=lambda kv: (
        len(kv[1]), kv[0]), reverse=True))
    with open(INDIRECT_CDN_PROVIDER_DOMAINS, "w") as f:
        json.dump(result, f, indent=2)
    return result

def analyze_indirect_w_ca_cdn_third(indirect_cdn_domains):
    cdn_map=base_function.read_cdn_map()
    result = defaultdict(dict)
    private_analyzer=base_function.PrivateAnalyzer()
    for cdn, domain_list in indirect_cdn_domains.items():
        cname_list = cdn_map[cdn]
        if cdn not in result:
            result[cdn]["third"] = set()
            result[cdn]["private"] = set()
        for domain in domain_list:
            print(cdn, domain)
            got_answer = False
            for cname in cname_list:
                if private_analyzer.is_other_private(domain,cname):
                    result[cdn]["private"].add(domain)
                    got_answer = True
                    break
            if not got_answer:
                result[cdn]["third"].add(domain)
    for cdn, depen_info in result.items():
        depen_info["third"] = list(depen_info["third"])
        depen_info["private"] = list(depen_info["private"])
    with open(INDIRECT_CDN_THIRD_RESULT,"w") as f:
        json.dump(result,f,indent=2)
    return result

def analyze_indirect_w_ca_cdn_critical(indirect_w_cdn_depen):
    result = defaultdict(dict)
    for w,cdn_list in indirect_w_cdn_depen.items():
        for cdn in cdn_list:
            if cdn not in result:
                result[cdn]["critical"] = set()
                result[cdn]["noncritical"] = set()
            if len(cdn_list) > 1:
                result[cdn]["noncritical"].add(w)
            else:
                result[cdn]["critical"].add(w)
    for ns, depen_info in result.items():
        depen_info["critical"] = list(depen_info["critical"])
        depen_info["noncritical"] = list(depen_info["noncritical"])
        result[ns] = depen_info
    result = dict(sorted(result.items(), key=lambda kv:
                  len(kv[1]["critical"])+len(kv[1]["noncritical"]), reverse=True))
    with open(INDIRECT_CDN_CRITICAL_RESULT,"w") as f:
        json.dump(result,f,indent=2)
    return result



def main():
    with open(DIRECT_W_CA_PATH, "r") as f:
        direct_ca_data = json.load(f)
    print("-----Get CA URL of CA-----")
    ca_url_dict = get_ca_url_dict(direct_ca_data)
    print("-----Get CA CDN Dict-----")
    ca_cdn=get_cdn_of_caProvider(ca_url_dict)
    print("-----Get Indirect W-CA-CDN Depen-----")
    indirect_w_cdn_depen=get_indirect_w_ca_cdn_depen(ca_cdn)
    print("-----Get Indirect CDN Provider Domains-----")
    indirect_cdn_domains=get_indirect_cdn_provider_domains(indirect_w_cdn_depen)
    print("-----Analyzing Indirect CDN Third-----")
    third=analyze_indirect_w_ca_cdn_third(indirect_cdn_domains)
    print("-----Analyzing Indirect CDN Critical")
    critical=analyze_indirect_w_ca_cdn_critical(indirect_w_cdn_depen)
    print("-----Finish-----")

if __name__ == '__main__':
    main()
