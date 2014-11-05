#!/usr/bin/env python
import matplotlib.pyplot as plt
import matplotlib
import csv
import numpy as np
from plot import to_float

font = {
    'family': 'serif',
    'size': 18}

matplotlib.rc('font', **font)
dpi = plt.figure().dpi
matplotlib.rcParams.update({'figure.autolayout': True})

# http://www.mulinblog.com/a-color-palette-optimized-for-data-visualization/
colors = ['#5da5da', '#faa43a', '#60bd68', '#f17cb0', '#b2912f', '#b276b2']
path = "/Users/chushumo/Project/papers/2015-multiwayjoin/images"


def max_workload_plot():
    """
        Plot the maximum workload per server using different HC configs
    """
    # read data from csv
    with open("./csvs/SIGMOD Experiment - hcs_config.csv", "rU") as f:
        csvreader = csv.reader(f)
        data = [list(row) for row in csvreader]

    N = 4
    ind = np.arange(N)          # x locations
    bar_width = 0.27           # the width of the bars

    # prepare data
    raco_hc = []
    random_hc = []
    lp_round = []

    for row in data[1:]:
        opt = to_float(row[3])
        raco_hc.append(to_float(row[1])/opt)
        random_hc.append(to_float(row[2])/opt)
        lp_round.append(to_float(row[4])/opt)

    # set bars
    fig, ax = plt.subplots()
    data_groups = [raco_hc, lp_round, random_hc]
    bars = []
    for i, group in enumerate(data_groups):
        rect = ax.bar(
            ind+0.1+i*bar_width, group, width=bar_width, color=colors[i])
        bars.append(rect)

    # set labels
    ax.set_ylabel("Optimal Ratio")
    ax.set_xticks(ind+bar_width*2)
    ax.set_xticklabels(("Q1", "Q2", "Q3", "Q4"))
    ax.set_ylim((0, 7))

    # set bar labels
    for bar in bars:
        for rect in bar:
            height = rect.get_height()
            ax.text(
                rect.get_x()+rect.get_width()/2.,
                1.05*height, '%.2f' % height,
                ha='center', va='bottom', size=14)

    ax.legend(
        (bars[0][0], bars[1][0], bars[2][0]),
        ('Our Alg.', 'Round Down', 'Random(4096 cells)'),
        prop={'size': 15})

    output_path = "{}/hcs_max_workload.pdf".format(path)
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
    bars1 = ax.bar(ind, random_hc, width=bar_width, color=colors[0])
    bars2 = ax.bar(ind+bar_width, raco_hc, width=bar_width, color=colors[1])
    ax.set_ylim(0, 800)

    # set labels
    ax.set_ylabel("Total shuffle workload (million tuples)")
    ax.set_xticks(ind+bar_width)
    ax.set_xticklabels(("Q1", "Q2", "Q3", "Q4"))
    ax.legend(
        (bars1[0], bars2[0]),
        ('Random Allocation', 'Our Alg.'),
        prop={'size': 15})

    output_path = "{}/hcs_total_workload.pdf".format(path)
    print "outputing {}".format(output_path)
    plt.savefig(output_path, format='pdf', dpi=dpi)

if __name__ == "__main__":
    max_workload_plot()
    #total_shuffle_plot()
