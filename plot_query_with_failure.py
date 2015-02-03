import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import csv
from plot import to_float

"""
    some queries may fail, so it worth specical treatment.
"""

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
query = "fb_q5"


def plot_q4_runtime(algebras, data, output_name):
    # plot wall clock time
    runtime = []    # query runtime
    std = []        # standard deviation
    for row in data:
        if row[0] == query:
            runtime.append(to_float(row[2]))
            std.append(to_float(row[3]))

    ind = np.arange(len(runtime))  # the x locations for the groups
    fig, ax = plt.subplots()
    rects = ax.bar(ind+0.1, runtime, width=bar_width, color=colors,  yerr=std)
    ax.set_ylabel('Time (sec)')
    ax.set_xticks(ind+xstick_offset)
    ax.set_xticklabels(algebras)
    ax.set_ylim((0, 14000))
    # label the bars
    for rect in rects:
        height = rect.get_height()
        if int(height) == 0:
            ax.text(
                rect.get_x()+rect.get_width()/2.,
                1.05*height, "FAIL",
                ha='center', va='bottom')
        else:
            ax.text(
                rect.get_x()+rect.get_width()/2.,
                1.05*height, '%d' % int(height),
                ha='center', va='bottom')
    print "outputing {}".format(output_name)
    plt.savefig(output_name, format='pdf', dpi=dpi)


def plot_q4_cpu(algebras, data, output_name):
    # plot wall clock time
    cputime = []    # query cputime
    for row in data:
        if row[0] == query:
            cputime.append(to_float(row[8]))

    ind = np.arange(len(cputime))  # the x locations for the groups
    fig, ax = plt.subplots()
    rects = ax.bar(ind+0.1, cputime, width=bar_width, color=colors)
    ax.set_ylabel('CPU Time (sec)')
    ax.set_xticks(ind+xstick_offset)
    ax.set_xticklabels(algebras)
    ax.set_ylim((0, 290000))
    # label the bars
    for rect in rects:
        height = rect.get_height()
        if int(height) == 0:
            ax.text(
                rect.get_x()+rect.get_width()/2.,
                1.05*height, "FAIL",
                ha='center', va='bottom')
        else:
            ax.text(
                rect.get_x()+rect.get_width()/2.,
                1.05*height, '%d' % int(height),
                ha='center', va='bottom')
    print "outputing {}".format(output_name)
    plt.savefig(output_name, format='pdf', dpi=dpi)


def plot_q4_shuffle(algebras, data, output_name):
    shuffle_size = []
    for row in data:
        if row[0] == query:
            shuffle_size.append(to_float(row[10]))
    ind = np.arange(len(shuffle_size))  # the x locations for the groups
    fig, ax = plt.subplots()
    rects = ax.bar(ind+0.1, shuffle_size, width=bar_width, color=colors)
    ax.set_ylabel('Tuples shuffled (million)')
    # ax.set_xlabel('Physical Algebra')
    ax.set_xticks(ind+xstick_offset)
    ax.set_xticklabels(algebras)
    ax.set_ylim((0, 16000))
    # label the bar
    for rect in rects:
        height = rect.get_height()
        if int(height) == 0:
            ax.text(
                rect.get_x()+rect.get_width()/2.,
                1.05*height, "FAIL",
                ha='center', va='bottom')
        else:
            ax.text(
                rect.get_x()+rect.get_width()/2.,
                1.05*height, '%d' % int(height),
                ha='center', va='bottom')
    print "outputing {}".format(output_name)
    plt.savefig(output_name, format='pdf', dpi=dpi)


def plot():
    fname = "csvs/SIGMOD Experiment - summary.csv"
    agbrs = ('RS_HJ', 'HC_HJ', 'BR_HJ', 'RS_TJ', 'HC_TJ', 'BR_TJ')
    with open(fname, "rU") as f:
        csvreader = csv.reader(f)
        data = [r for r in csvreader]
    plot_q4_runtime(agbrs, data, "{}/{}_wall_time.pdf".format(
        path, query))
    plot_q4_cpu(agbrs, data, "{}/{}_cpu_time.pdf".format(
        path, query))
    plot_q4_shuffle(agbrs, data, "{}/{}_shuffle_size.pdf".format(
        path, query))


if __name__ == '__main__':
    plot()
