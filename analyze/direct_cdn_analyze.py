import json
import csv
from collections import defaultdict

CDN_DATA_PATH="../data/direct_cdn/all_cdn_data.txt"
CDN_DEPENDENCY_RESULT_PATH = "../result/direct_cdn_analyze.txt"
CDN_PROVIDER_RESULT_PATH = "../result/direct_cdn_provider_analyze.txt"
CDN_PROVIDER_CSV_PATH = "../result/direct_cdn_provider_analyze.csv"

def get_has_cdn_num(cdn_info):
    has_cdn_num = 0
    if cdn_info["cdn"]:
        has_cdn_num = 1
    return has_cdn_num

def get_third_num(cdn_info):
    third_num = 0
    
    if cdn_info["third"]:
        third_num = 1
    return third_num

def get_multiple_third_cdn_num(cdn_info):
    #需要分析third中的实体个数
    multi_third_num = 0
    if len(cdn_info["third"]) > 1:
        multi_third_num = 1
    return multi_third_num

def get_critical_depen_num(cdn_info):
    #如果没有private cdn,且third ns的实体数量<=1,就认为是critical的
    critical_num = 0
    if cdn_info["critical"]:
        critical_num = 1
    return critical_num

def get_redundancy_num(cdn_info):
    #同时有多个third_ns，或者同时有private和third
    redundancy_num = 0
    if len(cdn_info["third"]) > 1 or (len(cdn_info["third"]) == 1 and len(cdn_info["private"]) > 0):
        redundancy_num = 1
    return redundancy_num


def get_rank_data(cdn_data, max_rank, result):
    if max_rank == "all":
        result_rank_str = "all"
    else:
        result_rank_str = "top_"+str(max_rank)
    result[result_rank_str]["has_cdn"] = 0
    result[result_rank_str]["third"] = 0
    result[result_rank_str]["multi_third"] = 0
    result[result_rank_str]["critical"] = 0
    result[result_rank_str]["redundancy"] = 0

    for domain, cdn_info in cdn_data.items():
        rank = int(cdn_info["rank"])
        if max_rank == "all":
            result[result_rank_str]["has_cdn"] += get_has_cdn_num(cdn_info)
            result[result_rank_str]["third"] += get_third_num(cdn_info)
            result[result_rank_str]["multi_third"] += get_multiple_third_cdn_num(cdn_info)
            result[result_rank_str]["critical"] += get_critical_depen_num(cdn_info)
            result[result_rank_str]["redundancy"] += get_redundancy_num(cdn_info)
        else:
            if rank < max_rank:
                result[result_rank_str]["has_cdn"] += get_has_cdn_num(cdn_info)
                result[result_rank_str]["third"] += get_third_num(cdn_info)
                result[result_rank_str]["multi_third"] += get_multiple_third_cdn_num(cdn_info)
                result[result_rank_str]["critical"] += get_critical_depen_num(cdn_info)
                result[result_rank_str]["redundancy"] += get_redundancy_num(cdn_info)

def direct_cdn_dependency_analyze():
    with open(CDN_DATA_PATH,"r") as f:
        cdn_data=json.load(f)

    result=defaultdict(dict)
    result["total_num"] = len(cdn_data)
    for max_rank in [100,1000,10000,"all"]:
        get_rank_data(cdn_data,max_rank,result)
    with open(CDN_DEPENDENCY_RESULT_PATH,"w") as f:
        json.dump(result,f,indent=2)


def direct_cdn_provider_analyzer():
    result = defaultdict(dict)
    result_csv = list()
    result_csv.append(("source", "target", "weight"))
    with open(CDN_DATA_PATH,"r") as f:
        source_data=json.load(f)

    for domain,cdn_info in source_data.items():
        cdn_entity_list=cdn_info["third"]

        for cdn_entity in cdn_entity_list:
            result_csv.append((domain, cdn_entity, 1))
            if cdn_entity not in result:
                result[cdn_entity]["critical"] = list()
                result[cdn_entity]["noncritical"] = list()
            if cdn_info["critical"]:
                result[cdn_entity]["critical"].append(domain)
            else:
                result[cdn_entity]["noncritical"].append(domain)
    result = dict(sorted(result.items(), key=lambda kv: len(
        kv[1]["critical"])+len(kv[1]["noncritical"]), reverse=True))
    with open(CDN_PROVIDER_RESULT_PATH, "w") as f:
        json.dump(result, f, indent=2)
    with open(CDN_PROVIDER_CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for data in result_csv:
            writer.writerow(data)

def main():
    print("-----Analyze direct W-CDN dependency-----")
    direct_cdn_dependency_analyze()
    print("-----Get CDN  Provider Contentration CSV-----")
    direct_cdn_provider_analyzer()
    print("-----finish-----")

if __name__ == '__main__':
    main()
