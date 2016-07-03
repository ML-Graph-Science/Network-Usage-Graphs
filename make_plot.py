import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import numpy

import copy
import random
from operator import itemgetter

import modify_logs


def plot_busiest_days(dict_transfers, num_days_to_graph, parser):
    num_bins = 86400
    top_transfer_days = parser.get_busiest_days(dict_transfers, num_days_to_graph, True)

    for date, transfers in top_transfer_days.items():
        # plot_original_data(transfers, date, num_bins)
        plot_modified_data(transfers, date, num_bins)


def plot_original_data(transfers, date, num_bins, network_bandwidth, plots_folder):
    tmp_transfers = copy.deepcopy(transfers)

    # if network_bandwidth is True then bin the data using the bin_data_using_transfer_rates function
    if network_bandwidth is True:
        bins = modify_logs.bin_data_using_transfer_rates(None, num_bins, tmp_transfers, date)
    # else if it is False, then bin the data using the bin_data_using_concurrent_transfers function
    else:
        bins = modify_logs.bin_data_using_concurrent_transfers(None, num_bins, tmp_transfers, date)[-num_bins:]

    # plot statistics about the original bins:
    bin_values = [cur_bin.bytes for cur_bin in bins]
    mean_value = numpy.mean(bin_values)
    std_deviation = numpy.std(bin_values)
    median_value = numpy.median(bin_values)

    min_bin_idx, min_bin = modify_logs.get_min_bin(bins)
    max_bin_idx, max_bin = modify_logs.get_max_bin(bins)

    print("\nmin bin value: {}, max bin value: {}".format(min_bin.bytes, max_bin.bytes))
    print("average bin value: {}, median bin value: {}".format(mean_value, median_value))
    print("std deviation: {}".format(std_deviation))

    if network_bandwidth is True:
        bytes_in_megabyte = 1024 * 1024
        # convert bytes to megabytes
        for cur_bin in bins:
            cur_bin.bytes = float(cur_bin.bytes) / bytes_in_megabyte

        title = "Network Usage on {} - {} Transfers".format(date, len(tmp_transfers))
        plot_filename = "{}/orig_network_demand/{}_{}-transfers_original.png".format(plots_folder,
                                                                                     date, len(tmp_transfers))
        ylabel = 'Network Demand (MiB/S)'
    else:
        title = "Concurrent Transfers on {} - {} Transfers".format(date, len(tmp_transfers))
        plot_filename = "{}/orig_concurrent_transfers/{}_{}-transfers_original.png".format(plots_folder, date,
                                                                                           len(tmp_transfers))
        ylabel = '# Concurrent Transfers'

    make_line_plot(plot_filename, title, ylabel, bins)


def plot_modified_data(transfers, date, num_bins, network_bandwidth, plots_folder, non_flexible_jobs_percent=None):
    # min_price_range = 0.1
    # max_price_range = 0.8
    min_price_range = 0.0
    max_price_range = 1.0
    # if non_flexible_jobs_percent is None:
    #     non_flexible_jobs_percent = [0.5]
    if non_flexible_jobs_percent is int:
        non_flexible_jobs_percent = [non_flexible_jobs_percent]

    tmp_transfers = copy.deepcopy(transfers)

    # if network_bandwidth is True then bin the data using the bin_data_using_transfer_rates function
    if network_bandwidth is True:
        original_bins = modify_logs.bin_data_using_transfer_rates(None, num_bins, tmp_transfers, date)
    # else if it is False, then bin the data using the bin_data_using_concurrent_transfers function
    else:
        original_bins = modify_logs.bin_data_using_concurrent_transfers(None, num_bins, tmp_transfers, date)[-num_bins:]

    modify_logs.assign_max_prices(original_bins, tmp_transfers, min_price_range, max_price_range)

    # shuffle the temp transfer list so we can randomly divide the list
    random.shuffle(tmp_transfers)

    # for each hard_job_value in the list of percents, split the jobs, make the bins, and plot the results
    for hard_jobs_value in non_flexible_jobs_percent:

        # calculate the number of x and y transfers and make the appropriate lists
        x_count = round(len(tmp_transfers) * hard_jobs_value)
        x_transfers = tmp_transfers[:x_count]
        y_transfers = tmp_transfers[x_count:]

        # need to sort the lists by transfer request time
        x_transfers = sorted(x_transfers, key=itemgetter('request_time'))
        y_transfers = sorted(y_transfers, key=itemgetter('request_time'))

        # if network_bandwidth is True then bin the data using the bin_data_using_transfer_rates function
        if network_bandwidth is True:
            x_bins = modify_logs.bin_data_using_transfer_rates(None, num_bins, x_transfers, date)
            new_bins = modify_logs.bin_data_using_transfer_rates(x_bins, len(x_bins), y_transfers,
                                                                 date, max_prices=True)
        # else if it is False, then bin the data using the bin_data_using_concurrent_transfers function
        else:
            x_bins = modify_logs.bin_data_using_concurrent_transfers(None, num_bins, x_transfers, date)
            new_bins = modify_logs.bin_data_using_concurrent_transfers(x_bins, len(x_bins), y_transfers,
                                                                       date, max_prices=True)

        make_plot_with_modified_bins(original_bins, x_bins[-num_bins:], new_bins[-num_bins:], network_bandwidth,
                                     plots_folder, len(tmp_transfers), date, hard_jobs_value)


def make_plot_with_modified_bins(original_bins, x_bins, new_bins, network_bandwidth,
                                 plots_folder, len_transfers, date, non_flexible_jobs_percent):
    if network_bandwidth is True:
        bins = copy.deepcopy(original_bins)
        bytes_in_megabyte = 1024 * 1024
        # convert bytes to megabytes
        for cur_bin in bins:
            cur_bin.bytes = float(cur_bin.bytes) / bytes_in_megabyte
        for cur_bin in x_bins:
            cur_bin.bytes = float(cur_bin.bytes) / bytes_in_megabyte
        for cur_bin in new_bins:
            cur_bin.bytes = float(cur_bin.bytes) / bytes_in_megabyte

        title = "Network Usage on {} - {} Transfers".format(date, len_transfers)
        plot_filename = "{}/mod_network_demand/{}_{}-transfers_{:.2f}-hard_percent.png".\
            format(plots_folder, date, len_transfers, non_flexible_jobs_percent)
        log_file = "output_logs/mod_network_demand/{}_{}-transfers_{:.2f}-hard_percent.csv". \
            format(date, len_transfers, non_flexible_jobs_percent)
        ylabel = 'Network Demand (MiB/S)'
    else:
        bins = original_bins
        title = "Concurrent Transfers on {} - {} Transfers".format(date, len_transfers)
        plot_filename = "{}/mod_concurrent_transfers/{}_{}-transfers_{:.2f}-hard_percent.png".\
            format(plots_folder, date, len_transfers, non_flexible_jobs_percent)
        log_file = "output_logs/mod_concurrent_transfers/{}_{}-transfers_{:.2f}-hard_percent.csv". \
            format(date, len_transfers, non_flexible_jobs_percent)
        ylabel = '# Concurrent Transfers'

    make_line_plot(plot_filename, title, ylabel, bins, new_bins=new_bins)
    # make_plot.make_line_plot(plot_filename, title, ylabel, bins, new_bins=new_bins, x_bins=x_bins)

    with open(log_file, 'w') as the_file:
        for idx, cur_bin in enumerate(new_bins):
            the_file.write('{}, {}, {}, {}\n'.format(idx, cur_bin.start_t, cur_bin.end_t, cur_bin.bytes))


def make_line_plot(filename, title, ylabel, bins, new_bins=None, x_bins=None):

    fig, ax = plt.subplots()

    plt.xlabel('Time of Day')
    plt.ylabel(ylabel)
    plt.title(title)

    x = [cur_bin.start_t for cur_bin in bins]
    y = [cur_bin.bytes for cur_bin in bins]

    plt.plot(x, y, color='cornflowerblue', linestyle='-', linewidth=0.5, label='Transfers')

    if new_bins is not None:
        x = [cur_bin.start_t for cur_bin in new_bins]
        y = [cur_bin.bytes for cur_bin in new_bins]

        plt.plot(x, y, color='red', linestyle='-', linewidth=0.5, label='Modified Transfers')

    if x_bins is not None:
        x = [cur_bin.start_t for cur_bin in x_bins]
        y = [cur_bin.bytes for cur_bin in x_bins]

        plt.plot(x, y, color='green', linestyle='-', linewidth=0.5, label='X Transfers')

    if new_bins is not None and x_bins is not None:
        plt.legend(loc=9, bbox_to_anchor=(0.5, -0.1), ncol=3, borderaxespad=1.7)

    elif new_bins is not None or x_bins is not None:
        plt.legend(loc=9, bbox_to_anchor=(0.5, -0.1), ncol=2, borderaxespad=1.7)

    interval = 3
    xtick_list = [(bins[0].start_t + datetime.timedelta(hours=i*interval)) for i in range(int(24/interval))]
    ax.set_xticks(xtick_list)

    ax.xaxis.set_minor_locator(mpl.dates.HourLocator())
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))

    date_min = bins[0].start_t - datetime.timedelta(hours=1)
    date_max = bins[-1].end_t + datetime.timedelta(hours=1)
    ax.set_xlim(date_min, date_max)

    fig.autofmt_xdate()

    print("\nSaving plot to %s" % filename)

    verify_filename(filename)

    plt.savefig(filename, dpi=250)

    plt.close(fig)


# make sure the plot filename is valid (i.e. all of the parent directories exist)
def verify_filename(filename):
    for idx, cur_char in enumerate(filename):
        if cur_char is '/':
            cur_dir_path = filename[:idx]

            if not os.path.exists(cur_dir_path):
                os.makedirs(cur_dir_path)

