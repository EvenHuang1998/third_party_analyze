import json

NS_DATA="../result/direct_ns_provider_analyze.txt"
CDN_DATA = "../result/direct_cdn_provider_analyze.txt"
CA_DATA="../result/direct_ca_provider_analyze.txt"

NS_CDF="../result/direct_ns_provider_cdf.txt"
CDN_CDF="../result/direct_cdn_provider_cdf.txt"
CA_CDF="../result/direct_ca_provider_cdf.txt"

def get_cdf(filepath):
    result = dict()
    rank=0
    sum_now=0
    with open(filepath,"r") as f:
        source_data=json.load(f)
    for provider,info in source_data.items():
        rank+=1
        sum_now+=len(info["critical"])+len(info["noncritical"])
        result[rank]=sum_now
    result["total"]=sum_now
    return result

def store_cdf_data(filepath,result):
    with open(filepath,"w") as f:
        json.dump(result,f,indent=2)

def main():
    ns_result=get_cdf(NS_DATA)
    store_cdf_data(NS_CDF,ns_result)
    cdn_result=get_cdf(CDN_DATA)
    store_cdf_data(CDN_CDF,cdn_result)
    ca_result=get_cdf(CA_DATA)
    store_cdf_data(CA_CDF,ca_result)

if __name__ == '__main__':
    main()