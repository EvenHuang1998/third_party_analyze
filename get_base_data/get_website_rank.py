#coding: utf-8
from collections import defaultdict
import sys
import json

sys.path.append("D:\myfiles\code\\third_party_depen_analyze_final")
sys.path.append("../")
from utils import base_function

RAW_RANK_FILEPATH="../data/website_rank/"
FORMATTED_FILEPATH="../data/website_rank/"

def chunked_file_reader(fp,block_size=1024*1024*100):
    while True:
        chunk=fp.read(block_size)
        if not chunk:
            break
        yield chunk

def format_file():
    formatted_data=defaultdict(int)
    sub_line_num=0
    line_num=0
    #excluded_domains=["miwifi","tendawifi","localhost"]
    for i in range(1, 22):
        source_filepath = RAW_RANK_FILEPATH+"raw_data_"+str(i)
        with open(source_filepath,"r") as f:
            for line in f:
                sub_line_num+=1
                if sub_line_num==10000:
                    sub_line_num=0
                    line_num+=1
                    print(line_num)
                line=line.strip().split("\t")
                website=line[2]
                domain=base_function.extract_tld(website)
                if not domain:
                    continue
                domain=domain.lower()
                dns_type=line[3]
                success=line[9]
                if success and dns_type=="A":
                    formatted_data[domain]+=1
    formatted_data=dict(sorted(formatted_data.items(),key=lambda kv:(kv[1],kv[0]),reverse=True))
    with open(FORMATTED_FILEPATH+"website_rank2.txt","w") as f:
        json.dump(formatted_data,f, indent=2)

def main():
    # for i in range(1,22):
    #     source_filepath=RAW_RANK_FILEPATH+"raw_data_"+str(i)
    #     dest_filepath=FORMATTED_FILEPATH+"formatted_data_"+str(i)+".txt"
    
    format_file()

if __name__ == '__main__':
    main()
