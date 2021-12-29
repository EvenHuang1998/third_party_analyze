import matplotlib.pyplot as plt
import json
import numpy as np

def plot_ns_bar():
    with open("../result/direct_ns_analyze.txt","r") as f:
        ns_data=json.load(f)
    x_name = ["100", "1000", "10000", "20000"]
    x = np.arange(4)
    bar_width = 0.15
    x1 = x-bar_width/2
    x2 = x1+bar_width
    x3 = x1+2*bar_width
    x4 = x1+3*bar_width
    x_name_pos = x2+bar_width/2

    y_third = list()
    y_critical = list()
    y_redundancy = list()
    y_multi = list()

    top_str_list=["top_100","top_1000","top_10000","all"]
    for top_str in top_str_list:
        if top_str=="all":
            top_rank=20000
        else:
            top_rank=int(top_str.strip("top_"))
        print(top_rank)
        value=ns_data[top_str]
        y_third.append(value["third"]/top_rank*100)
        y_critical.append(value["critical"]/top_rank*100)
        y_redundancy.append(value["redundancy"]/top_rank*100)
        y_multi.append(value["multi_third"]/top_rank*100)
    print(y_third,y_critical,y_redundancy,y_multi)
    plt.ylim(0, 100)
    plt.bar(x1, y_third, bar_width, hatch="|||",
            label="3rd Party Dependency", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width
    plt.bar(x2, y_critical, bar_width, hatch="\\\\\\",
            label="Critical Dependency", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width
    plt.bar(x3, y_redundancy, bar_width, hatch="+++",
            label="Redundancy", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width
    plt.bar(x4, y_multi, bar_width, hatch="...",
            label="Multiple 3rd", color="white", edgecolor="black")

    plt.xticks(x_name_pos, x_name)

    for a, b in zip(x1, y_third):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7, rotation=90)
    for a, b in zip(x2, y_critical):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7, rotation=90)
    for a, b in zip(x3, y_redundancy):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7, rotation=90)
    for a, b in zip(x4, y_multi):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7, rotation=90)
    plt.grid(axis="y", linestyle="-.", alpha=0.4)
    #plt.legend(fontsize=10,ncol=2,loc="upper center")
    plt.legend(fontsize=10, bbox_to_anchor=(1.01, 0), loc=3, borderaxespad=0)

    plt.title("Direct Third Party DNS Provider Dependency Analyze")
    plt.xlabel("Alexa Rank")
    plt.ylabel("Percentage of Websites")
    plt.savefig("../result/images/direct_third_ns_analyze.jpg", bbox_inches='tight')
    plt.clf()

def plot_ca_bar():
    with open("../result/direct_ca_analyze.txt", "r") as f:
        ns_data = json.load(f)
    x_name = ["100", "1000", "10000", "20000"]
    x = np.arange(4)
    bar_width = 0.15
    x1 = x-bar_width/2
    x2 = x1+bar_width
    x3 = x1+2*bar_width
    x4 = x1+3*bar_width
    x_name_pos = x2+bar_width/2

    y_has_https = list()
    y_third_https = list()
    y_stapling = list()

    top_str_list = ["top_100", "top_1000", "top_10000", "all"]
    for top_str in top_str_list:
        if top_str == "all":
            top_rank = 20000
        else:
            top_rank = int(top_str.strip("top_"))
        print(top_rank)
        value = ns_data[top_str]
        y_has_https.append(value["has_https"]/top_rank*100)
        y_third_https.append(value["third"]/top_rank*100)
        y_stapling.append(value["ocsp_stapling"]/top_rank*100)
    print(y_has_https, y_third_https, y_stapling)
    #画图
    plt.ylim(0, 110)
    plt.bar(x1, y_has_https, bar_width, hatch="|||",
            label="Has HTTPS", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width
    plt.bar(x2, y_third_https, bar_width, hatch="\\\\\\",
            label="3rd Party Dependency", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width
    plt.bar(x3, y_stapling, bar_width, hatch="+++",
            label="Support OCSP Stapling", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width

    plt.xticks(x_name_pos, x_name)

    #给每个柱上标数据
    for a, b in zip(x1, y_has_https):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7, rotation=90)
    for a, b in zip(x2, y_third_https):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7, rotation=90)
    for a, b in zip(x3, y_stapling):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7, rotation=90)

    #设置画布的一些属性

    plt.legend(fontsize=10, bbox_to_anchor=(1.01, 0), loc=3, borderaxespad=0)

    plt.grid(axis="y", linestyle="-.", alpha=0.4)
    plt.title("Direct Third Party CA Provider Dependency Analyze")
    plt.xlabel("Alexa Rank")
    plt.ylabel("Percentage of Websites")
    plt.savefig("../result/images/direct_third_ca_analyze.jpg", bbox_inches='tight')
    plt.clf()

def plot_cdn_bar():
    with open("../result/direct_cdn_analyze.txt", "r") as f:
        ns_data = json.load(f)
    x_name = ["100", "1000", "10000", "20000"]
    x = np.arange(4)
    bar_width = 0.15
    x1 = x-bar_width/2
    x2 = x1+bar_width
    x3 = x1+2*bar_width
    x4 = x1+3*bar_width
    x_name_pos = x2+bar_width/2

    y_has_cdn = list()
    y_third = list()
    y_redundancy = list()
    y_multi=list()

    top_str_list = ["top_100", "top_1000", "top_10000", "all"]
    for top_str in top_str_list:
        if top_str == "all":
            top_rank = 20000
        else:
            top_rank = int(top_str.strip("top_"))
        print(top_rank)
        value = ns_data[top_str]
        y_has_cdn.append(value["has_cdn"]/top_rank*100)
        y_third.append(value["third"]/top_rank*100)
        y_redundancy.append(value["redundancy"]/top_rank*100)
        y_multi.append(value["multi_third"]/top_rank*100)
    print(y_has_cdn, y_third, y_redundancy,y_multi)
    #画图
    plt.ylim(0, 110)
    plt.bar(x1, y_has_cdn, bar_width, hatch="|||",
            label="Has CDN", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width
    print("ffff")
    print(x2, y_third)
    plt.bar(x2, y_third, bar_width, hatch="\\\\\\",
            label="3rd Party Dependency", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width
    plt.bar(x3, y_redundancy, bar_width, hatch="+++",
            label="Redundancy", color="white", edgecolor="black")
    for i in range(len(x)):
        x[i] += bar_width
    plt.bar(x4, y_multi, bar_width, hatch="...",
            label="Multiple 3rd", color="white", edgecolor="black")

    plt.xticks(x_name_pos, x_name)

    for a, b in zip(x1, y_has_cdn):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7, rotation=90)
    for a, b in zip(x2, y_third):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7, rotation=90)
    for a, b in zip(x3, y_redundancy):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7, rotation=90)
    for a, b in zip(x4, y_multi):
        plt.text(a, b+1, "%.2f" % b, ha='center',
                 va='bottom', fontsize=7, rotation=90)
    plt.legend(fontsize=10, bbox_to_anchor=(1.01, 0), loc=3, borderaxespad=0)
    plt.grid(axis="y", linestyle="-.", alpha=0.4)

    plt.title("Direct Third Party CDN Provider Dependency Analyze")
    plt.xlabel("Alexa Rank")
    plt.ylabel("Percentage of Websites")
    plt.savefig("../result/images/direct_third_cdn_analyze.jpg", bbox_inches='tight')
    plt.clf()

def main():
    print("-----Plot NS Bar-----")
    plot_ns_bar()
    print("-----Plot CA Bar-----")
    plot_ca_bar()
    print("-----Plot CDN Bar-----")
    plot_cdn_bar()
    print("-----Finish-----")

if __name__ == '__main__':
    main()
