from collections import defaultdict
import json
import csv


CA_DATA_PATH = "../data/direct_ca/all_ca_data.txt"
CA_DEPENDENCY_RESULT_PATH = "../result/direct_ca_analyze.txt"
CA_PROVIDER_RESULT_PATH = "../result/direct_ca_provider_analyze.txt"
CA_PROVIDER_CSV_PATH = "../result/direct_ca_provider_analyze.csv"

def get_has_https_num(ca_info):
    return 1

def get_third_num(ca_info):
    third_num=0
    if ca_info["third"]:
        third_num=1
    return third_num

def get_ocsp_stapling_num(ca_info):
    ocsp_stapling_num=0
    if ca_info["ocsp stapling"]:
        ocsp_stapling_num=1
    return ocsp_stapling_num


def get_rank_data(ca_data, max_rank, result):
    if max_rank == "all":
        result_rank_str = "all"
    else:
        result_rank_str = "top_"+str(max_rank)
    result[result_rank_str]["has_https"] = 0
    result[result_rank_str]["third"] = 0
    result[result_rank_str]["ocsp_stapling"] = 0

    for domain, ca_info in ca_data.items():
        rank = int(ca_info["rank"])
        if max_rank == "all":
            result[result_rank_str]["has_https"] += get_has_https_num(ca_info)
            result[result_rank_str]["third"] += get_third_num(ca_info)
            result[result_rank_str]["ocsp_stapling"] += get_ocsp_stapling_num(ca_info)

        else:
            if rank < max_rank:
                result[result_rank_str]["has_https"] += get_has_https_num(ca_info)
                result[result_rank_str]["third"] += get_third_num(ca_info)
                result[result_rank_str]["ocsp_stapling"] += get_ocsp_stapling_num(ca_info)

def direct_ca_dependency_analyze():
    with open(CA_DATA_PATH,"r") as f:
        ca_data=json.load(f)
    result = defaultdict(dict)
    result["total_num"] = len(ca_data)
    for max_rank in [100, 1000, 10000, "all"]:
        get_rank_data(ca_data, max_rank, result)
    #print(result)

    with open(CA_DEPENDENCY_RESULT_PATH, "w") as f:
        json.dump(result, f, indent=2)


def direct_ca_provider_analyze():
    result = defaultdict(dict)
    result_csv = list()
    result_csv.append(("source", "target", "weight"))
    with open(CA_DATA_PATH, "r") as f:
        source_data = json.load(f)

    for domain, ca_info in source_data.items():
        ca_entity = ca_info["issuer"]["organizationName"]
        print(domain,ca_entity)
        result_csv.append((domain, ca_entity, 1))
        if ca_entity not in result:
            
            result[ca_entity]["critical"] = []
            result[ca_entity]["noncritical"] = []
        if ca_info["critical"]:
            result[ca_entity]["critical"].append(domain)
        else:
            result[ca_entity]["noncritical"].append(domain)
    result = dict(sorted(result.items(), key=lambda kv: len(
        kv[1]["critical"])+len(kv[1]["noncritical"]), reverse=True))
    with open(CA_PROVIDER_RESULT_PATH, "w") as f:
        json.dump(result, f, indent=2)
    with open(CA_PROVIDER_CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for data in result_csv:
            writer.writerow(data)

def main():
    print("-----Analyzing direct W-CA dependency")
    direct_ca_dependency_analyze()
    print("-----Get CA Provider Concentration CSV")
    direct_ca_provider_analyze()
    print("-----finish-----")

if __name__ == '__main__':
    main()
