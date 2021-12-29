import json

def process():
    with open("all_ns_data.txt","r") as f:
        source_data=json.load(f)
    for domain,ns_info in source_data.items():
        ns_entity_list=ns_info["ns_entity"]
        
        ns_name_list = ns_info["ns_entity_name"]
        for ns_entity in ns_entity_list:
            # if "taobao" in ns_entity or "alibaba" in ns_entity or "alidns" in ns_entity:
            #     ns_info["ns_entity_name"].append("ALIBABA")
            # if "aliyun" in ns_entity:
            #     ns_name_list.append("ALIBABA")
            # if "awsdns" in ns_entity:
            #     ns_name_list.append("AMAZON TECHNOLOGIES, INC.")
            # if "azure" in ns_entity:
            #     ns_name_list.append("MICROSOFT CORPORATION")
            # if "dnsv4"  in ns_entity or "dnspod" in ns_entity or "dnsv2" in ns_entity \
            #     or "dnsv3" in ns_entity:
            #     ns_name_list.append("DNSPOD")
            # if "hichina" in ns_entity:
            #     ns_name_list.append("ALIBABA")
            # if "dnsv5" in ns_entity:
            #     ns_name_list.append("DNSPOD")
            # if '"ns1.dns' in ns_entity and "dnsowl" not in ns_entity:
            #     ns_name_list.append("NSONE")
            # if "cloudflare" in ns_entity:
            #     ns_name_list.append("CLOUDFLARE")
            if "ns.yunjiasu" in ns_entity:
                ns_name_list.append(
                    "BEIJING BAIDU NETCOM SCIENCE TECHNOLOGY CO., LTD.")
        ns_info["ns_entity_name"]=list(set(ns_name_list))
    with open("all_ns_data.txt","w") as f:
        json.dump(source_data,f,indent=2)

if __name__ == '__main__':
    process() 
