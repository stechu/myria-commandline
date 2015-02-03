#!/usr/bin/env python
import matplotlib.pyplot as plt
import csv
import matplotlib
from plot import to_float

bar_width = 0.6
xstick_offset = 0.4

font = {
    'family': 'serif',
    'size': 21}

matplotlib.rc('font', **font)
dpi = plt.figure().dpi
matplotlib.rcParams.update({'figure.autolayout': True})
# http://www.mulinblog.com/a-color-palette-optimized-for-data-visualization/
colors = ['#5da5da', '#faa43a', '#60bd68', '#f17cb0', '#b2912f', '#b276b2']
path = "/Users/chushumo/Project/papers/2015-multiwayjoin/images"


def attrorder_plot():
    datafile = "csvs/SIGMOD Experiment - attr_order_sum.csv"
    with open(datafile, "rU") as f:
        reader = csv.reader(f)
        data = [list(row) for row in reader]
    plt.figure()
    data1 = [(to_float(row[1]), to_float(row[2]))
             for row in data[1:] if row[3] == "Q3"]
    cost1, time1 = zip(*data1)
    data2 = [(to_float(row[1]), to_float(row[2]))
             for row in data[1:] if row[3] == "Q4"]
    cost2, time2 = zip(*data2)
    fig, ax = plt.subplots()
    ax.scatter(cost1, time1, color=colors[0], s=80, label="Q3")
    ax.scatter(cost2, time2, color=colors[1], s=80, label="Q4")
    ax.set_xscale('log')
    plt.xlabel('Estimated cost')
    plt.ylabel('Actual running time (Sec)')
    ax.legend(prop={'size': 15})
    plt.axis([0, 10e22, -30, 1200])
    oname = "{}/attr_order_scatter.pdf".format(path)
    print "output to {}".format(oname)
    plt.savefig(oname, format='pdf')


if __name__ == '__main__':
    attrorder_plot()
