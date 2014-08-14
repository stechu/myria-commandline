#!/usr/bin/env python
import matplotlib.pyplot as plt
import csv


def attrorder_plot():
    datafile = "attr_order.csv"
    with open(datafile, "rU") as f:
        reader = csv.reader(f)
        data = [list(row) for row in reader]
    plt.figure()
    data = [row[:2] for row in data[1:]]
    cost, time = zip(*data)
    fig, ax = plt.subplots()
    ax.scatter(cost, time, s=50)
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.xlabel('Estimated cost')
    plt.ylabel('Actual running time')
    plt.axis([0, 10e18, 0, 1000])
    plt.savefig("attr_order_scatter.pdf", format='pdf')


if __name__ == '__main__':
    attrorder_plot()
