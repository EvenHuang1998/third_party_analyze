from collections import defaultdict
from time import sleep
import tldextract
import ssl
import certifi
import socket
import requests
import json
import sys
import os
sys.path.append("D:\myfiles\code\\third_party_depen_analyze_final")
sys.path.append("../")
from utils import base_function

DEST_FILEPATH="../data/direct_ca/"


def https_visit(domain):
    """
    Args:
        domain: the domain that needs to check https support.
    Returns:
        status: whether input domain supports https
        hostname: hostname(eg:"www.baidu.com") if domain supports https, else "".
    """
    hostname_www="www."+domain
    hostname_domain=domain
    https_www_url = "https://"+hostname_www
    https_url = "https://"+hostname_domain
    status,hostname=False,""
    try:
        requests.get(https_www_url,timeout=5, verify=False)
        status,hostname= True,hostname_www
    except:
        pass
    if not status:
        try:
            requests.get(https_url,timeout=5)
            status,hostname=True,hostname_domain
        except:
            pass
    return status,hostname
    
def get_all_https_support_data(rank_data):
    """
    Args:
        rank_data: dict of rank data
    Returns:
        A dict of domains support https and the hostname that should be visited to get https.
        
        example:
        {
            "baidu.com":"https://www.baidu.com"
        }
    """
    all_https_support_data=defaultdict(dict)
    for rank,domain in rank_data.items():
        print(rank,domain)
        status,hostname=https_visit(domain)
        if status:
            all_https_support_data[domain]["rank"]=rank
            all_https_support_data[domain]["hostname"]=hostname
        sleep(1)
    filename=DEST_FILEPATH+"https_support.txt"
    with open(filename,"w") as f:
        json.dump(all_https_support_data,f,indent=2)
    return all_https_support_data


def ssl_ctx():
    """
    Args:

    Returns:
        context that is needed to get CA.
    """
    sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
    sslctx.verify_mode = ssl.CERT_REQUIRED
    sslctx.check_hostname = False
    sslctx.load_verify_locations(certifi.where())
    return sslctx


def get_ca(context, hostname):
    """
    Args:
        context: the context to get CA. It was returned by function ssl_ctx().
        hostname: the hostname that is used to establish https connection, eg: baidu.com,www.baidu.com.
    Returns:
        status: whether the CA is successfully obtained.
        cert: CA of the hostname.
    """
    status,cert=False,None
    try:
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
        status,cert= True, cert
    except:
        pass
    return status,cert


def format_ca(ca):
    formatted_ca = dict()

    issued_to = dict()
    if "subject" in ca:
        for sub in ca["subject"]:
            issued_to[sub[0][0]] = sub[0][1]
    formatted_ca["issued_to"] = issued_to

    issuer = dict()
    if "issuer" in ca:
        for issue in ca["issuer"]:
            issuer[issue[0][0]] = issue[0][1]
    formatted_ca["issuer"] = issuer

    san_list = list()
    if "subjectAltName" in ca:
        for _, san in ca["subjectAltName"]:
            san_list.append(san)
    formatted_ca["san"] = san_list

    ocsp_list = list()
    if "OCSP" in ca:
        for ocsp in ca["OCSP"]:
            ocsp_list.append(ocsp)
    formatted_ca["ocsp"] = ocsp_list

    ca_url_list = list()
    if "caIssuers" in ca:
        for ca_url in ca["caIssuers"]:
            ca_url_list.append(ca_url)
    formatted_ca["ca_url"] = ca_url_list

    cdp_list = list()
    if "crlDistributionPoints" in ca:
        for cdp in ca["crlDistributionPoints"]:
            cdp_list.append(cdp)
    formatted_ca["cdp"] = cdp_list

    return formatted_ca

def get_all_ca_data(all_https_data):
    ctx=ssl_ctx()
    all_ca_data=defaultdict(dict)
    for domain,hostname_info in all_https_data.items():
        hostname=hostname_info["hostname"]
        rank=hostname_info["rank"]
        print(rank,domain,hostname)
        status,cert=get_ca(ctx,hostname)
        if status:
            all_ca_data[domain] = format_ca(cert)
            all_ca_data[domain]["rank"] = rank
            #print(all_ca_data[domain])
        sleep(2)
    filename=DEST_FILEPATH+"ca.txt"
    with open(filename,"w") as f:
        json.dump(all_ca_data,f,indent=2)
    return all_ca_data


def analyze_ca_third(result):
    private_analyzer = base_function.PrivateAnalyzer()
    for domain,ca_info in result.items():
        rank=ca_info["rank"]
        print(rank,domain)
        third=list()
        private=list()
        ca_url=""
        if "ca_url" in ca_info and ca_info["ca_url"]:
            ca_url=ca_info["ca_url"][0]
        issuer = ""
        if "issuer" in ca_info and "organizationName" in ca_info["issuer"]:
            issuer=ca_info["issuer"]["organizationName"]
        if ca_url and issuer:
            if private_analyzer.is_other_private(domain,ca_url):
                private.append(issuer)
            else:
                third.append(issuer)
        result[domain]["private"]=private
        result[domain]["third"]=third
    return result


def ocsp_stapling(hostname):
    with os.popen("./is_ca_critical.sh "+hostname) as process:
        output = process.read()
    
    if "OCSP Response Status: successful" in output:
        result = True
    else:
        result = False
    return result


def website_visit(website):
    try:
        requests.get(website, timeout=5)
        return "OK"
    except:
        return "ERROR"

def get_website(domain):
    http_www_domain = "https://www."+domain
    http_domain = "https://"+domain
    if website_visit(http_www_domain) == "OK":
        website = http_www_domain
    elif website_visit(http_domain) == "OK":
        website = http_domain
    else:
        website = ""
    return website


def extract_hostname(website):
    try:
        ext = tldextract.extract(website)
        return ext.subdomain+"."+ext.registered_domain
    except:
        return ""

def analyze_ca_critical(result):
    analyzed_num=0
    for domain,ca_info in result.items():
        rank=ca_info["rank"]
        print(rank,domain)
        
        website=get_website(domain)
        hostname = extract_hostname(website)
        #if website:
        stapling=ocsp_stapling(hostname)
        result[domain]["ocsp stapling"] = True if stapling else False
        result[domain]["critical"]=False if stapling else True
        analyzed_num+=1
        if analyzed_num%100==0:
            num=analyzed_num//100
            filename=DEST_FILEPATH+"tmp_ca_"+str(num)+".txt"
            print("Stored Temporary CA",filename )
            with open(filename,"w") as f:
                json.dump(result,f,indent=2)
        sleep(2)
    return result

def main():
    # print("-----load rank data-----")
    # rank_data=base_function.load_rank_data()
    # print("-----get https support data-----")
    # all_https_support_data=get_all_https_support_data(rank_data)
    # print("-----get all ca data-----")
    # result=get_all_ca_data(all_https_support_data)
    with open(DEST_FILEPATH+"ca.txt","r") as f:
        result=json.load(f)
    print("-----analyze ca third-----")
    result=analyze_ca_third(result)
    print("-----analyze ca critical-----")
    result=analyze_ca_critical(result)
    print("-----store ca data-----")
    filename=DEST_FILEPATH+"all_ca_data.txt"
    with open(filename,"w") as f:
        json.dump(result,f,indent=2)
    print("-----finish ca-----")

if __name__ == '__main__':
    main()
