#!/usr/bin/env python
import matplotlib.pyplot as plt
import matplotlib
import csv
import numpy as np

bar_width = 0.6
xstick_offset = 0.4

font = {
    'family': 'serif',
    'size': 18}

matplotlib.rc('font', **font)
dpi = plt.figure().dpi
matplotlib.rcParams.update({'figure.autolayout': True})
# http://www.mulinblog.com/a-color-palette-optimized-for-data-visualization/
colors = ['#5da5da', '#faa43a', '#60bd68', '#f17cb0', '#b2912f', '#b276b2']
path = "/Users/chushumo/Project/papers/2015-multiwayjoin/images"


def scl_plot():
    with open("csvs/SIGMOD Experiment - scalability_summary.csv", "rU") as f:
        csvreader = csv.reader(f)
        data = [list(row) for row in csvreader]
    head = data[0]
    data = data[1:]
    workers = [r[0] for r in data]
    # filter
    head = head[1:3]
    data = [row[1:3] for row in data]
    hc_spd_up = []
    rs_spd_up = []
    opt_spd_up = [1, 2, 4, 8, 16, 32]
    # transform data to speed up
    for row in data:
        hc_spd_up.append(
            float(data[0][0])/float(row[0]))
        rs_spd_up.append(
            float(data[0][1])/float(row[1]))
    locs = np.arange(len(data))
    markers = ['o', 'v']
    ax = plt.gca()
    line1 = ax.plot(
        locs, rs_spd_up, marker=markers[0], markersize=15, color=colors[0])
    line2 = ax.plot(
        locs, hc_spd_up, marker=markers[1], markersize=15, color=colors[1])
    line3 = ax.plot(
        locs, opt_spd_up, linestyle='--', color='r')
    ax.set_xlabel('Number of workers')
    ax.set_xlim([0, 5.1])
    ax.set_ylabel('Speed up')
    ax.set_yscale('log', basey=2)
    ax.set_xticklabels(workers)
    ax.legend(
        (line1[0], line2[0], line3[0]),
        ('HC_TJ', 'RS_HJ', 'opt.'),
        prop={'size': 15})
    ofile_name = "{}/scalability_time.pdf".format(
        path)
    print "outputing {}".format(ofile_name)
    plt.savefig(ofile_name, format='pdf')


def scl_plot_resource():
    with open("csvs/scalability_plot.csv", "rU") as f:
        csvreader = csv.reader(f)
        data = [list(row) for row in csvreader]
    head = data[0]
    data = data[1:]
    workers = [r[0] for r in data]
    #filter
    head = head[4:7]
    data = [r[4:7] for r in data]
    locs = list(range(len(data)))
    markers = ['o', '^', 's']
    plt.figure()
    for i, label in enumerate(head):
        plt_data = [r[i] for r in data]
        plt.plot(
            locs, plt_data, marker=markers[i], markersize=15,
            linestyle='--', color=colors[-i], label=label)
    plt.xlabel('Number of workers')
    plt.ylabel('Ratio')
    plt.axis([-0.2, 5.2, 0, 4])
    plt.xticks(locs, workers)
    plt.legend(prop={'size': 15})
    ofile_name = "{}/scalability_resource.pdf".format(path)
    print "outputing {}".format(ofile_name)
    plt.savefig(ofile_name, format='pdf')


if __name__ == '__main__':
    scl_plot()
    #scl_plot_resource()
