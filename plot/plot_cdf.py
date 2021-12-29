import matplotlib.pyplot as plt
import json

def plot_ns_cdf():
    with open("../result/direct_ns_provider_cdf.txt","r") as f:
        source_data=json.load(f)
    y=list()
    total=int(source_data["total"])
    for rank,num in source_data.items():
        if rank!="total":
            y.append(num/total)
    #print(y)
    x=range(len(y))
    plt.plot(x,y)
    plt.title("CDF of DNS Provider")
    plt.xlabel("Number of DNS Provider")
    plt.ylabel("CDF of Websites")
    plt.savefig("../result/images/direct_ns_provider_cdf.jpg")
    plt.clf()


def plot_ca_cdf():
    with open("../result/direct_ca_provider_cdf.txt", "r") as f:
        source_data = json.load(f)
    y = list()
    total = int(source_data["total"])
    for rank, num in source_data.items():
        if rank != "total":
            y.append(num/total)
    #print(y)
    x = range(len(y))
    plt.plot(x, y)
    plt.title("CDF of CA Provider")
    plt.xlabel("Number of CA Provider")
    plt.ylabel("CDF of Websites")
    plt.savefig("../result/images/direct_ca_provider_cdf.jpg")
    plt.clf()


def plot_cdn_cdf():
    with open("../result/direct_cdn_provider_cdf.txt", "r") as f:
        source_data = json.load(f)
    y = list()
    total = int(source_data["total"])
    for rank, num in source_data.items():
        if rank != "total":
            y.append(num/total)
    #print(y)
    x = range(len(y))
    #print(x)
    plt.plot(x, y)
    plt.title("CDF of CDN Provider")
    plt.xlabel("Number of CDN Provider")
    plt.ylabel("CDF of Websites")
    plt.savefig("../result/images/direct_cdn_provider_cdf.jpg")
    plt.clf()

def main():
    plot_ns_cdf()
    plot_ca_cdf()
    plot_cdn_cdf()

if __name__ == '__main__':
    main()
