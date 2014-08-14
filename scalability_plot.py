#!/usr/bin/env python
import matplotlib.pyplot as plt
import csv


def scl_plot():
    with open("scalability_plot.csv", "rU") as f:
        csvreader = csv.reader(f)
        data = [list(row) for row in csvreader]
    head = data[0]
    data = data[1:]
    workers = [r[0] for r in data]
    # filter
    head = head[1:3]
    data = [row[1:3] for row in data]
    locs = list(range(len(data)))
    markers = ['.', 'o', 'v', '^', 's', 'p']
    colors = ['b', 'g', 'r', 'c', 'm', 'y']
    plt.figure()
    for i, label in enumerate(head):
        plt_data = [r[i] for r in data]
        plt.plot(
            locs, plt_data, marker=markers[i],
            linestyle='--', color=colors[i], label=label)
    plt.xlabel('Number of workers')
    plt.ylabel('Ratio')
    plt.xticks(locs, workers)
    plt.title('Scalability')
    plt.legend()
    print "outputing {}".format("scalability_time.pdf")
    plt.savefig("scalability_time.pdf", format='pdf')


def scl_plot_resource():
    with open("scalability_plot.csv", "rU") as f:
        csvreader = csv.reader(f)
        data = [list(row) for row in csvreader]
    head = data[0]
    data = data[1:]
    workers = [r[0] for r in data]
    #filter
    head = head[4:7]
    data = [r[4:7] for r in data]
    locs = list(range(len(data)))
    markers = ['.', 'o', 'v', '^', 's', 'p']
    colors = ['b', 'g', 'r', 'c', 'm', 'y']
    plt.figure()
    for i, label in enumerate(head):
        plt_data = [r[i] for r in data]
        plt.plot(
            locs, plt_data, marker=markers[i],
            linestyle='--', color=colors[i], label=label)
    plt.xlabel('Number of workers')
    plt.ylabel('Ratio')
    plt.axis([-0.2, 5.2, 0, 4])
    plt.xticks(locs, workers)
    plt.title('Scalability')
    plt.legend()
    print "outputing {}".format("scalability_resource.pdf")
    plt.savefig("scalability_resource.pdf", format='pdf')


if __name__ == '__main__':
    scl_plot()
    scl_plot_resource()
