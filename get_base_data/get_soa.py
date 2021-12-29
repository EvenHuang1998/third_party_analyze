import dns.resolver
import sys
import json
sys.path.append("D:\myfiles\code\\third_party_depen_analyze_final")
sys.path.append("../")
from utils import base_function
DEST_FILEPATH="../data/"

def main():
    rank_data=base_function.load_rank_data()
    soa_data=dict()
    print("-----get soa-----")
    for rank,domain in rank_data.items():
        print(rank,domain)
        soa_data[domain]=base_function.get_soa(domain)
    filename=DEST_FILEPATH+"soa.txt"
    with open(filename,"w") as f:
        json.dump(soa_data,f,indent=2)

if __name__=='__main__':
    main()