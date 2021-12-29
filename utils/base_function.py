from collections import defaultdict
import tldextract
import dns.resolver
import whois
import json
import re

RANK_FILEPATH = "../data/website_rank/"
CA_FILEPATH ="../data/direct_ca/"
SOA_FILEPATH="../data/"
CDN_MAP_PATH = "../data/cdnMap"
#RANK_FILEPATH="./data/website_rank"
def load_rank_data():
    """
    Returns:
        A dict of ranked domain information.
        
        example:
        {
            1:"google.com",
            2:"baidu.com"
        }
    """
    source_filename = RANK_FILEPATH+"formated_website_rank.txt"
    with open(source_filename, "r") as f:
        rank_data = json.load(f)
    return rank_data

def load_ca():
    """
    Args:

    Returns:
        ca dict read from data directory.
    """
    ca_filename = CA_FILEPATH+"all_ca_data.txt"
    with open(ca_filename,"r") as f:
        ca_data=json.load(f)
    
    return ca_data


def load_soa():
    """
    Args:

    Returns:
        soa dict read from data directory.
    """
    soa_filename = SOA_FILEPATH+"soa.txt"
    with open(soa_filename, "r") as f:
        soa_data = json.load(f)
    return soa_data

def extract_tld(url):
    """
    Args:
        url: valid url
    Returns:
        TLD of input url
        
        example:
            "google.com"
    """
    try:
        ext =  tldextract.extract(url)
        tld = ext.registered_domain
    except:
        tld = ""
    return tld

def get_soa(domain):
    """
    Args:
        domain: valid TLD of a website
    Returns:
        rname
        mname
    """
    rname=""
    mname=""
    try:
        answer=dns.resolver.resolve(domain,"SOA")
        rname=str(answer[0].rname)
        mname=str(answer[0].mname)
    except:
        pass
    return [rname,mname]


def tld_in_san(tld, san_list):
    regrex = ".*"+tld
    for san in san_list:
        if re.match(regrex, san):
            return True
    return False

def whois_query(website):
    """
    Args:
        website: FQDN of a website.
    Returns:
        Whois organization the website belongs to.
        If something wrong happened or dict key is wrong, it returns "".
    """
    org = ""
    try:
        w = whois.whois(website)
        if "org" in w:
            org = w["org"].upper()
        elif "organization" in w:
            org = w["organization"].upper()
        elif "registrant_name" in w:
            org = w["registrant_name"].upper()
        elif "registrant_organization" in w:
            org = w['registrant_organization'].upper()
        elif 'registrant_org' in w:
            org = w['registrant_org'].upper()
        elif 'tech_org' in w:
            org = w['tech_org'].upper()
        else:
            org = ""
        if "PRIVACY" in org or "REDACTED" in org:
            org=""
    except:
        org = "whois_error"
    return org


def read_cdn_map():
    """
    Args:
    Returns:None. But this function updates self.cdn_map_dict property.
        updated data example:
        {
            "Google":["google.com","googlehosted.com"]
        }
    """
    cdn_map_dict=dict()
    with open(CDN_MAP_PATH, "r") as f:
        for line in f:
            line = line.strip().split(",")
            cdn, cname_list = line[0], line[1].split(' ')
            cdn_map_dict[cdn] = cname_list
    return cdn_map_dict

def get_ns_entity_name(entity):
    org=whois_query(entity)
    if not org or org=="whois_error":
        if "awsdns" in entity:
            org="AMAZON TECHNOLOGIES, INC."
        elif "dnsv" in entity or "dnspod" in entity:
            org="DNSPOD"
        elif "alidns" in entity or "taobao" in entity or "alibabadns" in entity or "aliyun" in entity:
            org="ALIBABA"
        elif "akam" in entity:
            org="AKAMAI TECHNOLOGIES, INC."
        elif "cloudflare" in entity:
            org="CLOUDFLARE"
        else:
            org=extract_tld(entity)
    return org


class PrivateAnalyzer(object):
    def __init__(self):
        self.ca_dict=load_ca()
        self.soa_dict=load_soa()

    def get_san(self,domain):
        san=list()
        if domain in self.ca_dict:
            san=self.ca_dict[domain]["san"]
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
            soa=get_soa(domain)
        return soa

    def is_other_private(self,domain,other):
        tld_domain = extract_tld(domain)
        tld_other=extract_tld(other)
        if tld_domain and tld_other and tld_domain == tld_other:
            return True
        san=self.get_san(domain)
        if tld_in_san(tld_other,san):
            return True
        soa_domain=self.get_soa(domain)
        soa_other=self.get_soa(tld_other)
        if soa_domain and soa_other and soa_domain==soa_other:
            return True
        return False


class NsDivider(object):
    """
    This class is used to divide NS in a list into serveral parties depend on which enetity
    it belongs to.

    Attributes:
        arr_: list of NSes.
    """

    def __init__(self, arr_):
        self.arr = arr_
        self.parent = [i for i in range(len(arr_))]
        self.ns_entity = set()
        self.ns_entity_num = len(arr_)
        self.ns_info = defaultdict(dict)

    def __get_ns_info(self):
        for ns in self.arr:
            ns_tld = extract_tld(ns)
            self.ns_info[ns]["tld"] = ns_tld
            self.ns_info[ns]["rname"], self.ns_info[ns]["mname"] = get_soa( ns_tld)

    def belong_to_same_entity(self, ns1, ns2):
        tld1 = self.ns_info[ns1]["tld"]
        tld2 = self.ns_info[ns2]["tld"]
        if tld1 and tld2 and tld1 == tld2:
            return True
        rname1, mname1 = self.ns_info[ns1]["rname"], self.ns_info[ns1]["mname"]
        rname2, mname2 = self.ns_info[ns2]["rname"], self.ns_info[ns2]["mname"]
        if rname1 and rname2 and rname1 == rname2:
            return True
        if mname1 and mname2 and mname1 == mname2:
            return True
        return False

    def find(self, i):
        root = i
        while root != self.parent[root]:
            root = self.parent[root]
        while i != root:
            parent_ = self.parent[i]
            self.parent[i] = root
            i = parent_
        return root

    def union(self, i, j):
        root_i, root_j = self.find(i), self.find(j)
        if self.belong_to_same_entity(self.arr[i], self.arr[j]) and root_i != root_j:
            if root_i <= root_j:
                self.parent[j] = self.parent[i]
            else:
                self.parent[i] = self.parent[j]

    def divide(self):
        n = len(self.arr)
        self.__get_ns_info()
        for i in range(n):
            for j in range(i+1, n):
                self.union(i, j)
        for p_index in set(self.parent):
            self.ns_entity.add(self.arr[p_index])
        self.ns_entity_num = len(set(self.parent))

