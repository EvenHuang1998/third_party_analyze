from re import L
import matplotlib.pyplot as plt
import numpy as np
import json

DIRECT_NS_RESULT="../data/direct_ns/all_ns_data.txt"
DIRECT_NS_PROVIDER = "../result/direct_ns_provider_analyze.txt"
INDIRECT_CA_NS_PROVIDER = "../result/indirect_ca_ns/indirect_ns_name_critical.txt"

DIRECT_CDN_RESULT = "../data/direct_cdn/all_cdn_data.txt"
DIRECT_CDN_PROVIDER = "../result/direct_cdn_provider_analyze.txt"
INDIRECT_CA_CDN_PROVIDER = "../result/indirect_ca_cdn/indirect_cdn_critical.txt"

INDIRECT_CDN_NS_PROVIDER = "../result/indirect_cdn_ns/indirect_ns_name_critical.txt"

def get_top_n_providers(source_data,n):
    """
    Get top N most visited providers in indirect data.
    """
    top_n_provider = list()
    num = 0
    for provider, _ in source_data.items():
        num += 1
        if num > n:
            break
        top_n_provider.append(provider)
    return top_n_provider

def get_y_only_c(direct_data, top_n_providers, total_domain_num):
    y_only_c = list()
    for provider in top_n_providers:
        domain_num = len(direct_data[provider]["critical"]) + \
            len(direct_data[provider]["noncritical"])
        y_only_c.append(domain_num/total_domain_num)
    y_only_c = [y*100 for y in y_only_c]
    return y_only_c

def get_y_both_c(direct_data, indirect_data, top_n_providers, total_domain_num):
    y_both_c = list()
    for provider in top_n_providers:
        domain_set = set()
        domain_set = domain_set.union(
            direct_data[provider]["critical"]+direct_data[provider]["noncritical"])
        if provider in indirect_data:
            domain_set = domain_set.union(
                indirect_data[provider]["critical"]+indirect_data[provider]["noncritical"])
        domain_num = len(domain_set)
        y_both_c.append(domain_num/total_domain_num)
    y_both_c = [y*100 for y in y_both_c]
    return y_both_c

def get_y_only_i(direct_data, top_n_providers, total_domain_num):
    y_only_i = list()
    for provider in top_n_providers:
        domain_num = len(direct_data[provider]["critical"])
        y_only_i.append(domain_num/total_domain_num)
    y_only_i = [y*100 for y in y_only_i]
    return y_only_i

def get_y_both_i(direct_data, indirect_data, top_n_providers, total_domain_num):
    y_both_i = list()
    for provider in top_n_providers:
        domain_set = set()
        domain_set = domain_set.union(direct_data[provider]["critical"])
        if provider in indirect_data:
            domain_set = domain_set.union(indirect_data[provider]["critical"])
        domain_num = len(domain_set)
        y_both_i.append(domain_num/total_domain_num)
    y_both_i = [y*100 for y in y_both_i]
    return y_both_i

def plot_ca_dns_c_bar():
    with open(INDIRECT_CA_NS_PROVIDER,"r") as f:
        indirect_data=json.load(f)
    with open(DIRECT_NS_PROVIDER,"r") as f:
        direct_data=json.load(f)
    with open(DIRECT_NS_RESULT,"r") as f:
        direct_ns=json.load(f)
    total_domain_num=len(direct_ns)

    #CHANGED
    top_n = 5
    top_n_providers = get_top_n_providers(direct_data,top_n)
    x_name = top_n_providers
    x = np.arange(top_n)

    bar_width = 0.3
    x1 = x-bar_width/2
    x2 = x1+bar_width
    x_name_pos = x1+bar_width/2

    y_only_c=get_y_only_c(direct_data,top_n_providers,total_domain_num)
    y_both_c=get_y_both_c(direct_data,indirect_data,top_n_providers,total_domain_num)

    plt.ylim(0, 100)
    plt.bar(x1, y_only_c, bar_width, hatch="\\\\\\",
            label="Web->DNS", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width
    plt.bar(x2, y_both_c, bar_width, hatch="...",
            label="Web->DNS∪Web->CA->DNS", color="white", edgecolor="black")
    for a, b in zip(x1, y_only_c):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7)
    for a, b in zip(x2, y_both_c):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7)
    plt.xticks(x_name_pos, x_name)
    plt.grid(axis="y", linestyle="-.", alpha=0.4)
    plt.xlabel("DNS Provider")
    plt.ylabel("Percentage of Websites")
    plt.legend(fontsize=10, loc="upper center")
    plt.savefig("../result/images/indirect_ca_dns_c.jpg", bbox_inches='tight')
    plt.clf()

def plot_ca_dns_i_bar():
    with open(INDIRECT_CA_NS_PROVIDER, "r") as f:
        indirect_data = json.load(f)
    with open(DIRECT_NS_PROVIDER, "r") as f:
        direct_data = json.load(f)
    with open(DIRECT_NS_RESULT, "r") as f:
        direct_ns = json.load(f)
    total_domain_num = len(direct_ns)

    top_n = 5
    top_n_providers = get_top_n_providers(direct_data, top_n)
    x_name = top_n_providers
    x = np.arange(top_n)

    bar_width = 0.3
    x1 = x-bar_width/2
    x2 = x1+bar_width
    x_name_pos = x1+bar_width/2

    y_only_i = get_y_only_i(direct_data, top_n_providers, total_domain_num)
    y_both_i = get_y_both_i(direct_data, indirect_data,
                            top_n_providers, total_domain_num)

    plt.ylim(0, 100)
    plt.bar(x1, y_only_i, bar_width, hatch="\\\\\\",
            label="Web->DNS", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width
    plt.bar(x2, y_both_i, bar_width, hatch="...",
            label="Web->DNS∪Web->CA->DNS", color="white", edgecolor="black")
    for a, b in zip(x1, y_only_i):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7)
    for a, b in zip(x2, y_both_i):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7)
    plt.xticks(x_name_pos, x_name)
    plt.grid(axis="y", linestyle="-.", alpha=0.4)
    plt.xlabel("DNS Provider")
    plt.ylabel("Percentage of Websites")
    plt.legend(fontsize=10, loc="upper center")
    plt.savefig("../result/images/indirect_ca_dns_i.jpg", bbox_inches='tight')
    plt.clf()

def plot_ca_cdn_c_bar():
    with open(INDIRECT_CA_CDN_PROVIDER, "r") as f:
        indirect_data = json.load(f)
    with open(DIRECT_CDN_PROVIDER, "r") as f:
        direct_data = json.load(f)
    with open(DIRECT_CDN_RESULT, "r") as f:
        direct_cdn = json.load(f)
    total_domain_num = len(direct_cdn)

    top_n = 5
    top_n_providers = get_top_n_providers(direct_data, top_n)
    x_name = top_n_providers
    x = np.arange(top_n)

    bar_width = 0.3
    x1 = x-bar_width/2
    x2 = x1+bar_width
    x_name_pos = x1+bar_width/2

    y_only_c = get_y_only_c(direct_data, top_n_providers, total_domain_num)
    y_both_c = get_y_both_c(direct_data, indirect_data,
                            top_n_providers, total_domain_num)

    plt.ylim(0, 100)
    plt.bar(x1, y_only_c, bar_width, hatch="\\\\\\",
            label="Web->CDN", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width
    plt.bar(x2, y_both_c, bar_width, hatch="...",
            label="Web->CDN∪Web->CA->CDN", color="white", edgecolor="black")
    for a, b in zip(x1, y_only_c):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7)
    for a, b in zip(x2, y_both_c):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7)

    plt.xticks(x_name_pos, x_name)
    plt.grid(axis="y", linestyle="-.", alpha=0.4)
    plt.xlabel("CDN Provider")
    plt.ylabel("Percentage of Websites")
    plt.legend(fontsize=10, loc="upper center")
    plt.savefig("../result/images/indirect_ca_cdn_c.jpg", bbox_inches='tight')
    plt.clf()

def plot_ca_cdn_i_bar():
    with open(INDIRECT_CA_CDN_PROVIDER, "r") as f:
        indirect_data = json.load(f)
    with open(DIRECT_CDN_PROVIDER, "r") as f:
        direct_data = json.load(f)
    with open(DIRECT_CDN_RESULT, "r") as f:
        direct_cdn = json.load(f)
    total_domain_num = len(direct_cdn)

    top_n = 5
    top_n_providers = get_top_n_providers(direct_data, top_n)
    x_name = top_n_providers
    x = np.arange(top_n)

    bar_width = 0.3
    x1 = x-bar_width/2
    x2 = x1+bar_width
    x_name_pos = x1+bar_width/2

    y_only_i = get_y_only_i(direct_data, top_n_providers, total_domain_num)
    y_both_i = get_y_both_i(direct_data, indirect_data,
                            top_n_providers, total_domain_num)

    plt.ylim(0, 100)
    plt.bar(x1, y_only_i, bar_width, hatch="\\\\\\",
            label="Web->CDN", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width
    plt.bar(x2, y_both_i, bar_width, hatch="...",
            label="Web->CDN∪Web->CA->CDN", color="white", edgecolor="black")
    for a, b in zip(x1, y_only_i):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7)
    for a, b in zip(x2, y_both_i):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7)
    plt.xticks(x_name_pos, x_name)
    plt.grid(axis="y", linestyle="-.", alpha=0.4)
    plt.xlabel("CDN Provider")
    plt.ylabel("Percentage of Websites")
    plt.legend(fontsize=10, loc="upper center")
    plt.savefig("../result/images/indirect_ca_cdn_i.jpg", bbox_inches='tight')
    plt.clf()

def plot_cdn_ns_c_bar():
    with open(INDIRECT_CDN_NS_PROVIDER, "r") as f:
        indirect_data = json.load(f)
    with open(DIRECT_NS_PROVIDER, "r") as f:
        direct_data = json.load(f)
    with open(DIRECT_NS_RESULT, "r") as f:
        direct_ns = json.load(f)
    total_domain_num = len(direct_ns)

    top_n = 5
    top_n_providers = get_top_n_providers(direct_data, top_n)
    #top_n_providers = get_top_n_providers(indirect_data, top_n)
    x_name = top_n_providers
    x = np.arange(top_n)

    bar_width = 0.3
    x1 = x-bar_width/2
    x2 = x1+bar_width
    x_name_pos = x1+bar_width/2

    y_only_c = get_y_only_c(direct_data, top_n_providers, total_domain_num)
    y_both_c = get_y_both_c(direct_data, indirect_data,
                            top_n_providers, total_domain_num)
    plt.ylim(0, 100)
    plt.bar(x1, y_only_c, bar_width, hatch="\\\\\\",
            label="Web->DNS", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width
    plt.bar(x2, y_both_c, bar_width, hatch="...",
            label="Web->DNS∪Web->CDN->DNS", color="white", edgecolor="black")
    for a, b in zip(x1, y_only_c):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7)
    for a, b in zip(x2, y_both_c):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7)
    plt.xticks(x_name_pos, x_name)
    plt.grid(axis="y", linestyle="-.", alpha=0.4)
    plt.xlabel("DNS Provider")
    plt.ylabel("Percentage of Websites")
    plt.legend(fontsize=10, loc="upper center")
    plt.savefig("../result/images/indirect_cdn_dns_c.jpg", bbox_inches='tight')
    plt.clf()

def plot_cdn_ns_i_bar():
    with open(INDIRECT_CDN_NS_PROVIDER, "r") as f:
        indirect_data = json.load(f)
    with open(DIRECT_NS_PROVIDER, "r") as f:
        direct_data = json.load(f)
    with open(DIRECT_NS_RESULT, "r") as f:
        direct_ns = json.load(f)
    total_domain_num = len(direct_ns)

    top_n = 5
    top_n_providers = get_top_n_providers(direct_data, top_n)
    x_name = top_n_providers
    x = np.arange(top_n)

    bar_width = 0.3
    x1 = x-bar_width/2
    x2 = x1+bar_width
    x_name_pos = x1+bar_width/2

    y_only_i = get_y_only_i(direct_data, top_n_providers, total_domain_num)
    y_both_i = get_y_both_i(direct_data, indirect_data,
                            top_n_providers, total_domain_num)

    plt.ylim(0, 100)
    plt.bar(x1, y_only_i, bar_width, hatch="\\\\\\",
            label="Web->DNS", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width
    plt.bar(x2, y_both_i, bar_width, hatch="...",
            label="Web->DNS∪Web->CDN->DNS", color="white", edgecolor="black")

    for a, b in zip(x1, y_only_i):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7)
    for a, b in zip(x2, y_both_i):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7)
    plt.xticks(x_name_pos, x_name)
    plt.grid(axis="y", linestyle="-.", alpha=0.4)
    plt.xlabel("DNS Provider")
    plt.ylabel("Percentage of Websites")
    plt.legend(fontsize=10, loc="upper center")
    plt.savefig("../result/images/indirect_cdn_dns_i.jpg", bbox_inches='tight')
    plt.clf()

def main():
    print("-----Plot CA-DNS C Bar-----")
    plot_ca_dns_c_bar()
    print("-----Plot CA-DNS I Bar-----")
    plot_ca_dns_i_bar()
    print("-----Plot CA-CDN C Bar-----")
    plot_ca_cdn_c_bar()
    print("-----Plot CA-CDN I Bar-----")
    plot_ca_cdn_i_bar()
    print("-----Plot CDN-DNS C Bar-----")
    plot_cdn_ns_c_bar()
    print("-----Plot CDN-DNS I Bar-----")
    plot_cdn_ns_i_bar()
    print("-----Finish-----")

if __name__ == '__main__':
    main()
