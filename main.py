import sys
from os.path import isfile

import parse_logs
import make_plot
import modify_logs
import datetime
import copy

def main():
    '''Main function'''

    if len(sys.argv) != 2:
        print("Received %d arguments - Expected 1" % (len(sys.argv) - 1))
        raise SystemExit

    file_name = sys.argv[1]

    # if len(sys.argv) > 2:
    #     print("Received %d arguments - Expected 1" % (len(sys.argv) - 1))
    #     raise SystemExit
    # elif len(sys.argv) is 2:
    #     file_name = sys.argv[1]
    # else:
    #     file_name = "globus_log.csv"

    print(file_name)

    if isfile(file_name) and file_name.endswith(".csv"):
        file_name = file_name
    elif isfile(file_name):
        print("Input file_name is not a .csv file - %s" % (file_name))
        raise SystemExit
    else:
        print("Input string is not a valid file_name - %s" % (file_name))
        raise SystemExit

    (header, transfers) = parse_logs.parse_csv(file_name, False)

    dict_transfers = parse_logs.dictify_rows(transfers)

    # transfers_by_day = parse_logs.get_transfers_by_day(dict_transfers, True)
    # transfers_per_day = parse_logs.get_transfers_per_day(dict_transfers, True)
    # max_date, max_count = parse_logs.get_max_day(dict_transfers, True)
    # transfers = parse_logs.get_transfers_on_day(dict_transfers, max_date)

    # make modified plots of the N busiest days for all of the transfers
    # plot_busiest_days(dict_transfers, num_days_to_graph=10)

    # print out all of the transfers that occur on the provided day sorted in descending order by the transfer rate
    # parse_logs.print_transfers_on_day(dict_transfers, date_to_print=datetime.date(2015, 7, 2))

    date_to_use = datetime.date(2015, 6, 3)
    transfers = parse_logs.get_transfers_on_day(dict_transfers, date_to_use)

    # plot_original_data(transfers, date_to_use, 86400, network_bandwidth=True)
    # plot_original_data(transfers, date_to_use, 86400, network_bandwidth=False)
    # plot_modified_data(transfers, date_to_use, 86400, network_bandwidth=True)
    # plot_modified_data(transfers, date_to_use, 86400, network_bandwidth=False)

    plot_modified_data(transfers, date_to_use, 86400, network_bandwidth=False, non_flexible_jobs_percent=0.05)
    plot_modified_data(transfers, date_to_use, 86400, network_bandwidth=False, non_flexible_jobs_percent=0.1)
    plot_modified_data(transfers, date_to_use, 86400, network_bandwidth=False, non_flexible_jobs_percent=0.2)
    plot_modified_data(transfers, date_to_use, 86400, network_bandwidth=False, non_flexible_jobs_percent=0.3)
    plot_modified_data(transfers, date_to_use, 86400, network_bandwidth=False, non_flexible_jobs_percent=0.4)


def plot_busiest_days(dict_transfers, num_days_to_graph):
    num_bins = 86400
    top_transfer_days = parse_logs.get_busiest_days(dict_transfers, num_days_to_graph, True)

    for date, transfers in top_transfer_days.items():
        # plot_original_data(transfers, date, num_bins)
        plot_modified_data(transfers, date, num_bins)


def plot_original_data(transfers, date, num_bins, network_bandwidth):
    tmp_transfers = copy.deepcopy(transfers)

    # if network_bandwidth is True then bin the data using the bin_data_using_transfer_rates function
    if network_bandwidth is True:
        bins = modify_logs.bin_data_using_transfer_rates(None, num_bins, tmp_transfers, date)
    # else if it is False, then bin the data using the bin_data_using_concurrent_transfers function
    else:
        bins = modify_logs.bin_data_using_concurrent_transfers(None, num_bins, tmp_transfers, date)

    if network_bandwidth is True:
        bytes_in_megabyte = 1024 * 1024
        # convert bytes to megabytes
        for cur_bin in bins:
            cur_bin.bytes = float(cur_bin.bytes) / bytes_in_megabyte

        title = "Network Usage on {} - {} Transfers".format(date, len(tmp_transfers))
        plot_filename = "plots/orig_network_demand/{}_{}-transfers_{}-bins.png".format(date, len(tmp_transfers), num_bins)
        ylabel = 'Network Demand (MiB/S)'
    else:
        title = "Concurrent Transfers on {} - {} Transfers".format(date, len(tmp_transfers))
        plot_filename = "plots/orig_concurrent_transfers/{}_{}-transfers_{}-bins.png".format(date, len(tmp_transfers),
                                                                                            num_bins)
        ylabel = '# Concurrent Transfers'

    make_plot.make_line_plot(plot_filename, title, ylabel, bins)


def plot_modified_data(transfers, date, num_bins, network_bandwidth, non_flexible_jobs_percent=None):
    min_price = 0.1
    max_price = 0.8
    if non_flexible_jobs_percent is None:
        non_flexible_jobs_percent = 0.5

    tmp_transfers = copy.deepcopy(transfers)

    bins, x_bins, new_bins = modify_logs.split_logs_and_modify_transfers(num_bins, tmp_transfers, date, min_price,
                                                                         max_price, non_flexible_jobs_percent,
                                                                         network_bandwidth=network_bandwidth)
    if network_bandwidth is True:
        bytes_in_megabyte = 1024 * 1024
        # convert bytes to megabytes
        for cur_bin in bins:
            cur_bin.bytes = float(cur_bin.bytes) / bytes_in_megabyte
        for cur_bin in x_bins:
            cur_bin.bytes = float(cur_bin.bytes) / bytes_in_megabyte
        for cur_bin in new_bins:
            cur_bin.bytes = float(cur_bin.bytes) / bytes_in_megabyte

        title = "Network Usage on {} - {} Transfers".format(date, len(tmp_transfers))
        plot_filename = "plots/mod_network_demand/{}_{}-transfers_{}-hard_percent.png".format(date, len(tmp_transfers),
                                                                                              non_flexible_jobs_percent)
        ylabel = 'Network Demand (MiB/S)'
        log_file = 'output_logs/mod_network_demand/{}-transfers_{}.csv'.format(len(tmp_transfers), date)
    else:
        title = "Concurrent Transfers on {} - {} Transfers".format(date, len(tmp_transfers))
        plot_filename = "plots/mod_concurrent_transfers/{}_{}-transfers_{}-hard_percent.png".\
            format(date, len(tmp_transfers), non_flexible_jobs_percent)
        ylabel = '# Concurrent Transfers'
        log_file = 'output_logs/mod_concurrent_transfers/{}-transfers_{}.csv'.format(len(tmp_transfers), date)

    make_plot.make_line_plot(plot_filename, title, ylabel, bins, new_bins=new_bins)
    # make_plot.make_line_plot(plot_filename, title, ylabel, bins, new_bins=new_bins, x_bins=x_bins)

    with open(log_file, 'w') as the_file:
        for idx, cur_bin in enumerate(new_bins):
            the_file.write('{}, {}, {}, {}\n'.format(idx, cur_bin.start_t, cur_bin.end_t, cur_bin.bytes))


if __name__ == "__main__":
    main()
