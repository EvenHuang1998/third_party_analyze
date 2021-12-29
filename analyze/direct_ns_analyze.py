import json
import csv
from collections import defaultdict
import sys
sys.path.append("D:\myfiles\code\\third_party_depen_analyze_final")
sys.path.append("../")
from utils import base_function

NS_DATA_PATH="../data/direct_ns/all_ns_data.txt"
#NS_DATA_PATH = "D:\myfiles\code\\third_party_depen_analyze_final\data\direct_ns\\all_ns_data.txt"
NS_DEPENDENCY_RESULT_PATH="../result/direct_ns_analyze.txt"
NS_PROVIDER_RESULT_PATH="../result/direct_ns_provider_analyze.txt"
NS_PROVIDER_CSV_PATH="../result/direct_ns_provider_analyze.csv"

def get_third_num(ns_info):
    third_num = 0
    if ns_info["third"]:
        third_num = 1
    return third_num


def get_multiple_third_ns_num(ns_info):
    #需要分析third中的实体个数
    multi_third_num = 0
    if len(ns_info["third"]) > 1:
        multi_third_num = 1
    return multi_third_num


def get_critical_depen_num(ns_info):
    #如果没有private ns,且third ns的实体数量<1,就认为是critical的
    critical_num = 0
    if ns_info["critical"]:
        critical_num = 1
    return critical_num


def get_redudancy_num(ns_info):
    #同时有多个third_ns，或者同时有private和third
    redudancy_num = 0
    if len(ns_info["third"]) > 1 or (len(ns_info["third"])==1 and len(ns_info["private"])>0):
        redudancy_num = 1
    return redudancy_num


def get_both_third_private_num(ns_info):
    both_third_private_num = 0
    if len(ns_info["private"])>0 and len(ns_info["third"])>0:
        both_third_private_num = 1
    return both_third_private_num

def get_rank_data(ns_data,max_rank,result):
    if max_rank=="all":
        result_rank_str = "all"
    else:
        result_rank_str = "top_"+str(max_rank)
    result[result_rank_str]["third"] = 0
    result[result_rank_str]["multi_third"] = 0
    result[result_rank_str]["critical"] = 0
    result[result_rank_str]["redundancy"] = 0
    result[result_rank_str]["both"] = 0

    
    for domain, ns_info in ns_data.items():
        rank = int(ns_info["rank"])
        if max_rank=="all":
            result[result_rank_str]["third"] += get_third_num(ns_info)
            result[result_rank_str]["multi_third"] += get_multiple_third_ns_num(ns_info)
            result[result_rank_str]["critical"] += get_critical_depen_num(ns_info)
            result[result_rank_str]["redundancy"] += get_redudancy_num(ns_info)
            result[result_rank_str]["both"] += get_both_third_private_num(ns_info)
        else: 
            if rank<max_rank:
                result[result_rank_str]["third"] += get_third_num(ns_info)
                result[result_rank_str]["multi_third"] += get_multiple_third_ns_num(ns_info)
                result[result_rank_str]["critical"] += get_critical_depen_num(ns_info)
                result[result_rank_str]["redundancy"] += get_redudancy_num(ns_info)
                result[result_rank_str]["both"] += get_both_third_private_num(ns_info)

def direct_ns_dependency_analyze():
    with open(NS_DATA_PATH, "r") as f:
        ns_data = json.load(f)

    result = defaultdict(dict)
    result["total_num"]=len(ns_data)
    for max_rank in [100,1000,10000,"all"]:
        get_rank_data(ns_data,max_rank,result)
    #print(result)

    with open(NS_DEPENDENCY_RESULT_PATH, "w") as f:
        json.dump(result, f, indent=2)

def direct_ns_provider_analyze():
    result=defaultdict(dict)
    result_csv = list()
    result_csv.append(("source", "target", "weight"))
    with open(NS_DATA_PATH,"r") as f:
        source_data=json.load(f)

    for domain,ns_info in source_data.items():
        ns_entity_list=ns_info["third"]
        for ns_entity in ns_entity_list:
            #ns_entity_name=base_function.get_ns_entity_name(ns_entity)
            #result_csv.append((domain,ns_entity_name,1))
            if ns_entity not in result:
                result[ns_entity]["critical"] = list()
                result[ns_entity]["noncritical"]=list()
            if ns_info["critical"]:
                result[ns_entity]["critical"].append(domain)
            else:
                result[ns_entity]["noncritical"].append(domain)
    result_entity_name=defaultdict(dict)
    for ns_entity,domain_info in result.items():
        ns_entity_name=base_function.get_ns_entity_name(ns_entity)
        print(ns_entity,ns_entity_name)
        if ns_entity_name not in result_entity_name:
            result_entity_name[ns_entity_name]["critical"]=set()
            result_entity_name[ns_entity_name]["noncritical"]=set()
        result_entity_name[ns_entity_name]["critical"]=\
            result_entity_name[ns_entity_name]["critical"].union(
                set(domain_info["critical"])
            )
        result_entity_name[ns_entity_name]["noncritical"]=\
            result_entity_name[ns_entity_name]["noncritical"].union(
                set(domain_info["noncritical"])
            )
        #result_entity_name[ns_entity_name]=domain_info
        for domain in domain_info["critical"]:
            result_csv.append((domain,ns_entity_name,1))
        for domain in domain_info["noncritical"]:
            result_csv.append((domain,ns_entity_name,1))
    for ns_entity_name,domain_info in result_entity_name.items():
        domain_info["critical"]=list(domain_info["critical"])
        domain_info["noncritical"]=list(domain_info["noncritical"])
    result_entity_name=dict(sorted(result_entity_name.items(),key=lambda kv:len(kv[1]["critical"])+len(
        kv[1]["noncritical"]),reverse=True))
    with open(NS_PROVIDER_RESULT_PATH,"w") as f:
        json.dump(result_entity_name,f,indent=2)
    with open(NS_PROVIDER_CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer=csv.writer(f)
        for data in result_csv:
            writer.writerow(data)

def main():
    print("-----Analyze direct W-NS dependency-----")
    direct_ns_dependency_analyze()
    print("-----Get NS Provider Concentration-----")
    direct_ns_provider_analyze()
    print("-----finish-----")


if __name__ == '__main__':
    main()
