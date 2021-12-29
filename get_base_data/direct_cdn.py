#coding: utf-8

from collections import defaultdict
from selenium import webdriver
import requests
import tldextract
import dns.resolver
from time import sleep
import json
import sys

sys.path.append("D:\myfiles\code\\third_party_depen_analyze_final")
sys.path.append("../")
from utils import base_function

#PATH_TO_CHROMEDRIVER = "./chromedriver.exe"
PATH_TO_CHROMEDRIVER="./chromedriver"
DEST_FILEPATH="../data/direct_cdn/"


def website_visit(website):
    """
    Args:
        website: protocal+FQDN, eg: http://www.baidu.com
    Returns:
        If requests get succeeded, return OK, else Error
    """
    try:
        requests.get(website, timeout=5)
        return "OK"
    except:
        return "ERROR"

def get_website(domain):
    """
    Args:
        domain: TLD domain, eg: baidu.com
    Returns:
        website: protocal+FQDN, eg: http://www.baidu.com
    """
    http_www_domain = "http://www."+domain
    http_domain = "http://"+domain
    if website_visit(http_www_domain) == "OK":
        website = http_www_domain
    elif website_visit(http_domain) == "OK":
        website = http_domain
    else:
        website = ""
    return website

class InternalUrlObtainner(object):
    def __init__(self):
        self.driver = None
        self.url_list = list()
        self.ca_dict=dict()
        self.soa_dict=dict()

    def get_driver(self):
        """
        Args:
        
        Returns:
            None. But class property self.driver is set.
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless')

        #self.driver = webdriver.Chrome(PATH_TO_CHROMEDRIVER, options=options)
        self.driver=webdriver.Chrome(options=options)

    def load_ca_dict(self):
        self.ca_dict = base_function.load_ca()

    def load_soa_dict(self):
        self.soa_dict = base_function.load_soa()

    def get_san(self,domain):
        """
        Args:
            domain: TLD of a domain, eg: baidu.com
        Returns:
            list of SAN of the domain.
        """
        san=list()
        if domain in self.ca_dict:
            san= self.ca_dict[domain]["san"]
        return san

    def get_soa(self,domain):
        """
        Args:
            domain: TLD of a domain, eg:baidu.com
        Returns:
            SOA list of the domain.
        """
        soa=list()
        if domain in self.soa_dict:
            soa = self.soa_dict[domain]
        else:
            soa=base_function.get_soa(domain)
        return soa

    def is_link_internal(self,website,link):
        """
        Args:
            website: protocal+FQDN
            link: protocal+FQDN of link in a website
        Returns:
            Is the link internal.
        """
        tld_website=base_function.extract_tld(website)
        tld_link=base_function.extract_tld(link)
        if tld_website and tld_link and tld_website== tld_link:
            return True
        san=self.get_san(tld_website)
        if base_function.tld_in_san(tld_link,san):
            return True
        soa_website=self.get_soa(tld_website)
        soa_link=self.get_soa(tld_link)
        if soa_website and soa_link and soa_website==soa_link:
            return True
        return False

    def get_landing_page_internal_url(self, domain):
        """
        Args:
            domain: TLD, eg: baidu.com
        Returns:
            list of internal link of the landing page of website.
        """
        website=get_website(domain)
        link_set = set([website])
        try:
            self.driver.get(website)
            for url in self.driver.find_elements_by_xpath("//*[@href]"):
                link = url.get_attribute("href")
                if not link.startswith("javascript") and self.is_link_internal(website,link):
                    link_set.add(link)
        except:
            pass
        return list(link_set)

    def initialize(self):
        self.get_driver()
        self.load_ca_dict()
        self.load_soa_dict()

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
        self.cdn_map_dict=base_function.read_cdn_map()

#def get_internal_link_data(rank_data):
# def get_internal_link_data(domain):
#     """
#     Args:
#         rank_data: dict of rank data
#     Returns:
#         dict of all internal link list of a domain.
#         example: 
#         {
#             "baidu.com":["https://www.baidu.com","https://www.baidu.com"]
#         }
#         The dict only contains domain that successfully got its internal link
#     """
#     url_obtainner = InternalUrlObtainner()
#     url_obtainner.initialize()
#     internal_link_dict = defaultdict(dict)

    # for rank, domain in rank_data.items():
    #     print(rank, domain)
    #     rank=int(rank)
        # if rank<=10000:
            # internal_link_list = url_obtainner.get_landing_page_internal_url(domain)
            # if internal_link_list:
            #     internal_link_dict[domain]["rank"]=rank
            #     internal_link_dict[domain]["internal_url_list"] = internal_link_list
    #     if rank%10==0:
    #         filename=DEST_FILEPATH+"internal_link_"+str(rank)+'.txt'
    #         with open(filename,"w") as f:
    #             json.dump(internal_link_dict,f,indent=2)
    # filename=DEST_FILEPATH+"internal_link_top10000.txt"
    # with open(filename,"w") as f:
    #     json.dump(internal_link_dict,f,indent=2)
    # return internal_link_dict

# def get_cname_and_cdn_data(internal_link_data):
#     url_obtainner = InternalUrlObtainner()
#     url_obtainner.initialize()
#     internal_link_dict = defaultdict(dict)
    
#     cdn_data=defaultdict(dict)
#     cdn_extractor=CdnExtractor()
#     cdn_extractor.initialize()

#     for domain,link_info in internal_link_data.items():
#         print(domain)  
#         cname_set=set()
#         #link_list=internal_link_data[domain]["internal_url_list"]
        
#         link_list = url_obtainner.get_landing_page_internal_url(domain)
#         if not internal_link_list:
#             continue
#         for link in link_list:
#             cname_list=cdn_extractor.recursively_get_cname(link)
#             cname_set=cname_set.union(cname_list)
#         cdn_list=cdn_extractor.map_cname_list_to_cdn(list(cname_set))
#         cdn_set=set(cdn_list)
#         if cdn_set:
#             cdn_data[domain]["rank"] = link_info["rank"]
#             cdn_data[domain]["cdn"]=list(cdn_set)
#             cdn_data[domain]["cname"] = list(cname_set)
#         sleep(2)
#     filename=DEST_FILEPATH+"cdn_entity_name.txt"
#     with open(filename,"w") as f:
#         json.dump(cdn_data,f,indent=2)
#     return cdn_data

def get_cname_and_cdn_data(rank_data):
    url_obtainner = InternalUrlObtainner()
    url_obtainner.initialize()
    
    cdn_extractor=CdnExtractor()
    cdn_extractor.initialize()
    cdn_data=defaultdict(dict)

    for rank,domain in rank_data.items():
        if int(rank)>=12000 and int(rank)<=15000:
            print(rank, domain)
            link_list = url_obtainner.get_landing_page_internal_url(domain)
            if not link_list:
                continue
            cname_set = set()
            for link in link_list:
                cname_list = cdn_extractor.recursively_get_cname(link)
                cname_set = cname_set.union(cname_list)
            cdn_list = cdn_extractor.map_cname_list_to_cdn(list(cname_set))
            cdn_set = set(cdn_list)
            if cdn_set:
                cdn_data[domain]["rank"] = rank
                cdn_data[domain]["cdn"] = list(cdn_set)
                #cdn_data[domain]["cname"] = list(cname_set)
            if int(rank)%1000==0:
                filename = DEST_FILEPATH+"cdn_entity_name_top_"+rank+".txt"
                with open(filename, "w") as f:
                    json.dump(cdn_data, f, indent=2)
    filename=DEST_FILEPATH+"cdn_entity_name.txt"
    with open(filename,"w") as f:
        json.dump(cdn_data,f,indent=2)
    return cdn_data

def analyze_cdn_third(result):
    cdn_map=base_function.read_cdn_map()
    private_analyzer = base_function.PrivateAnalyzer()
    for domain,cdn_info in result.items():
        third=list()
        private=list()
        rank=cdn_info["rank"]
        print(rank,domain)
        for cdn in cdn_info["cdn"]:
            got_answer=False
            cname_list=cdn_map[cdn]
            for cname in cname_list:
                if private_analyzer.is_other_private(domain,cname):
                    private.append(cdn)
                    got_answer=True
                    break
            if not got_answer:
                third.append(cdn)
        result[domain]["third"]=third
        result[domain]["private"]=private
    return result

def analyze_cdn_critical(result):
    for domain,cdn_info in result.items():
        print(domain)
        if not cdn_info["private"] and len(cdn_info["third"])<2:
            result[domain]["critical"]=True
        else:
            result[domain]["critical"]=False
    return result

def main():
    print("-----load rank data-----")
    rank_data = base_function.load_rank_data()
    # print("-----get internal link data-----")
    # internal_link_data=get_internal_link_data(rank_data)
    # print("-----get cdn data-----")
    # result=get_cname_and_cdn_data(internal_link_data)
    # print("-----get cdn data-----")
    # result=get_cname_and_cdn_data(rank_data)
    with open("../data/direct_cdn/all_cdn_data.txt","r") as f:
        result=json.load(f)
    print("-----analyze cdn third-----")
    result=analyze_cdn_third(result)
    print("-----analyze cdn critical-----")
    result=analyze_cdn_critical(result)
    print("-----store cdn data-----")
    filename=DEST_FILEPATH+"all_cdn_data.txt"
    with open(filename,"w") as f:
        json.dump(result,f,indent=2)
    print("-----finish cdn-----")


if __name__ == '__main__':
    main()
