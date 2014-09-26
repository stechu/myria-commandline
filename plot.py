#!/usr/bin/env python
# a bar plot with errorbars
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import csv

bar_width = 0.6
xstick_offset = 0.3

font = {
    'family': 'serif',
    'size': 21}

matplotlib.rc('font', **font)
dpi = plt.figure().dpi
matplotlib.rcParams.update({'figure.autolayout': True})


def to_float(str):
    return float(str.replace(',', ''))


def plot_wc_time(algebras, time, std, output_name):
    """
    Plot wall clock time
    """
    assert len(algebras) == len(time)
    assert len(std) == len(time)
    ind = np.arange(len(time))  # the x locations for the groups
    fig, ax = plt.subplots()
    ax.bar(ind, time, width=bar_width, color='m', yerr=std)
    ax.set_ylabel('Time (sec)')
    # ax.set_xlabel('Physical Algebra')
    ax.set_xticks(ind+xstick_offset)
    ax.set_xticklabels(algebras)
    print "outputing {}".format(output_name)
    plt.savefig(output_name, format='pdf', dpi=dpi)


def plot_cpu_time(algebras, time, output_name):
    """
    Plot cpu time
    """
    assert len(algebras) == len(time)
    ind = np.arange(len(time))  # the x locations for the groups
    fig, ax = plt.subplots()
    ax.bar(ind, time, width=bar_width, color='m')
    ax.set_ylabel('Time (sec)')
    # ax.set_xlabel('Physical Algebra')
    ax.set_xticks(ind+xstick_offset)
    ax.set_xticklabels(algebras)
    print "outputing {}".format(output_name)
    plt.savefig(output_name, format='pdf', dpi=dpi)


def plot_shuffle_skew(algebras, skews, output_name):
    """
    Plot max skew among shuffles
    """
    assert len(algebras) == len(skews)
    ind = np.arange(len(skews))  # the x locations for the groups
    fig, ax = plt.subplots()
    ax.bar(ind, skews, width=bar_width, color='m')
    ax.set_ylabel('Skew (max/avg)')
    # ax.set_xlabel('Physical Algebra')
    ax.set_xticks(ind+xstick_offset)
    ax.set_xticklabels(algebras)
    print "outputing {}".format(output_name)
    plt.savefig(output_name, format='pdf', dpi=dpi)


def plot_shuffle_size(algebras, shuffle_size, output_name):
    """
    Plot shuffle size
    """
    assert len(algebras) == len(shuffle_size)
    ind = np.arange(len(shuffle_size))  # the x locations for the groups
    fig, ax = plt.subplots()
    ax.bar(ind, shuffle_size, width=bar_width, color='m')
    ax.set_ylabel('Tuples shuffled (million)')
    # ax.set_xlabel('Physical Algebra')
    ax.set_xticks(ind+xstick_offset)
    ax.set_xticklabels(algebras)
    print "outputing {}".format(output_name)
    plt.savefig(output_name, format='pdf', dpi=dpi)


def plot_output_skew(algebras, skews, output_name):
    """
    Plot max skew among output
    """
    assert len(algebras) == len(skews)
    ind = np.arange(len(skews))  # the x locations for the groups
    fig, ax = plt.subplots()
    ax.bar(ind, skews, width=bar_width, color='m')
    ax.set_ylabel('Skew (max/avg)')
    # ax.set_xlabel('Physical Algebra')
    ax.set_xticks(ind+xstick_offset)
    ax.set_xticklabels(algebras)
    print "outputing {}".format(output_name)
    plt.savefig(output_name, format='pdf', dpi=dpi)


def plot_hashtable_size(algebras, htsizes, output_name):
    """
    """
    assert len(algebras) == len(htsizes)
    ind = np.arange(len(htsizes))  # the x locations for the groups
    fig, ax = plt.subplots()
    ax.bar(ind, htsizes, width=bar_width, color='m')
    ax.set_ylabel('Memory usage (MB)')
    # ax.set_xlabel('Physical Algebra')
    ax.set_xticks(ind+xstick_offset)
    ax.set_xticklabels(algebras)
    print "outputing {}".format(output_name)
    plt.savefig(output_name, format='pdf', dpi=dpi)


def plot():
    fname = "csvs/SIGMOD Experiment - summary.csv"
    agbrs = ('RS_HJ', 'HC_HJ', 'BR_HJ', 'RS_LFJ', 'HC_LFJ', 'BR_LFJ')
    queries = ('triangle',  'clique', 'fb_q1')
    with open(fname, "rU") as f:
        csvreader = csv.reader(f)
        data = [r for r in csvreader]
        # output wall clock time
        for query in queries:
            time = []
            std = []
            for row in data:
                if row[0] == query:
                    time.append(to_float(row[2]))
                    std.append(to_float(row[3]))
            plot_wc_time(agbrs, time, std, "{}_wall_time.pdf".format(query))

        # output cpu time
        for query in queries:
            time = []
            for row in data:
                if row[0] == query:
                    time.append(to_float(row[8]))
            plot_cpu_time(agbrs, time, "{}_cpu_time.pdf".format(query))

        # output shuffle skew
        for query in queries:
            skews = []
            for row in data:
                if row[0] == query:
                    skews.append(to_float(row[7]))
            plot_shuffle_skew(
                agbrs, skews, "{}_shuffle_skew.pdf".format(query))

        # output number of tuples shuffled in total
        for query in queries:
            shuffle_sizes = []
            for row in data:
                if row[0] == query:
                    shuffle_sizes.append(to_float(row[10]))
            plot_shuffle_size(
                agbrs, shuffle_sizes, "{}_shuffle_size.pdf".format(query))

        # output output skew
        for query in queries:
            skews = []
            for row in data:
                if row[0] == query:
                    skews.append(to_float(row[11]))
            plot_shuffle_skew(
                agbrs, skews, "{}_output_skew.pdf".format(query))

        # output hash table size
        for query in queries:
            htsizes = []
            for row in data:
                if row[0] == query:
                    htsizes.append(to_float(row[9]))
            plot_hashtable_size(
                agbrs, htsizes, "{}_memory.pdf".format(query))

if __name__ == '__main__':
    plot()
