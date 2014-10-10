#!/usr/bin/env python
import matplotlib.pyplot as plt
import matplotlib
import csv
import numpy as np

font = {
    'family': 'serif',
    'size': 18}

matplotlib.rc('font', **font)
dpi = plt.figure().dpi
matplotlib.rcParams.update({'figure.autolayout': True})

def max_workload_plot():
    """
        Plot the maximum workload per server using different HC configs
    """
    # read data from csv
    with open("./csvs/SIGMOD Experiment - server allocation.csv", "rU") as f:
        csvreader = csv.reader(f)
        data = [list(row) for row in csvreader]
    
    N = 4
    ind = np.arange(N)          # x locations
    bar_width = 0.3             # the width of the bars

    # prepare data
    random_hc = list((float(n.replace(',', '')) for n in data[1][1:]))
    raco_hc = list((float(n.replace(',', '')) for n in data[2][1:]))

    # million 
    random_hc = [n/1000000 for n in random_hc]
    raco_hc = [n/1000000 for n in raco_hc]

    # set bars
    fig, ax = plt.subplots()
    bars1 = ax.bar(ind, random_hc, width=bar_width, color='r')
    bars2 = ax.bar(ind+bar_width, raco_hc, width=bar_width, color="y")

    # set labels
    ax.set_ylabel("Max workload (million tuples)");
    ax.set_xticks(ind+bar_width)
    ax.set_xticklabels(("Q1", "Q2", "Q3", "Q4"))
    ax.set_ylim(0, 13)
    
    ax.legend( (bars1[0], bars2[0]), ('Random Allocation', 'Our Alg.'));

    output_path = "./images/hcs_max_workload.pdf"
    print "outputing {}".format(output_path)
    plt.savefig(output_path, format='pdf', dpi=dpi)

def total_shuffle_plot():
    """
        Plot the total shuffle workload using different HC configs
    """
    # read data from csv
    with open("./csvs/SIGMOD Experiment - server allocation.csv", "rU") as f:
        csvreader = csv.reader(f)
        data = [list(row) for row in csvreader]
    
    N = 4
    ind = np.arange(N)          # x locations
    bar_width = 0.3             # the width of the bars

    # prepare data
    random_hc = list((float(n.replace(',', '')) for n in data[3][1:]))
    raco_hc = list((float(n.replace(',', '')) for n in data[4][1:]))

    # million 
    random_hc = [n/1000000 for n in random_hc]
    raco_hc = [n/1000000 for n in raco_hc]

    # set bars
    fig, ax = plt.subplots()
    bars1 = ax.bar(ind, random_hc, width=bar_width, color='r')
    bars2 = ax.bar(ind+bar_width, raco_hc, width=bar_width, color="y")
    ax.set_ylim(0, 800)

    # set labels
    ax.set_ylabel("Total shuffle workload (million tuples)");
    ax.set_xticks(ind+bar_width)
    ax.set_xticklabels(("Q1", "Q2", "Q3", "Q4"))
    ax.legend( (bars1[0], bars2[0]), ('Random Allocation', 'Our Alg.'));

    output_path = "./images/hcs_total_workload.pdf"
    print "outputing {}".format(output_path)
    plt.savefig(output_path, format='pdf', dpi=dpi)

if __name__ == "__main__":
    max_workload_plot()
    total_shuffle_plot()
