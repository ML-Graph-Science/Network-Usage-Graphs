import sys
from os.path import isfile, exists
from os import makedirs
import datetime

import parse_globus_logs
import parse_xfer_data_logs
import make_plot


def main():
    '''Main function'''

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Received %d arguments - Expected 1" % (len(sys.argv) - 1))
        raise SystemExit

    file_name = sys.argv[1]

    # if the user passes in the command line argument to use parse_xfer_data_logs then use that parser
    if len(sys.argv) == 3 and sys.argv[2] == 'parse_xfer_data_logs':
        parser = parse_xfer_data_logs
        plots_folder = 'plots-xfer_data_logs'
    # otherwise default to using parse_globus_logs as the parser for the program
    else:
        parser = parse_globus_logs
        plots_folder = 'plots-globus_logs'

    # verify that the plots output folder exists, if it doesn't, then create it
    if not exists(plots_folder):
        makedirs(plots_folder)

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

    (header, transfers) = parser.parse_csv(file_name, False)

    dict_transfers = parser.dictify_rows(transfers)

    # transfers_by_day = parse_logs.get_transfers_by_day(dict_transfers, True)
    # transfers_per_day = parse_logs.get_transfers_per_day(dict_transfers, True)
    # max_date, max_count = parse_logs.get_max_day(dict_transfers, True)
    # transfers = parse_logs.get_transfers_on_day(dict_transfers, max_date)

    # make modified plots of the N busiest days for all of the transfers
    # plot_busiest_days(dict_transfers, num_days_to_graph=10, parser)

    # print out all of the transfers that occur on the provided day sorted in descending order by the transfer rate
    # parse_logs.print_transfers_on_day(dict_transfers, date_to_print=datetime.date(2015, 7, 2))

    # date_to_use = datetime.date(2015, 6, 3)
    # transfers = parser.get_transfers_on_day(dict_transfers, date_to_use)

    # date_to_use = datetime.date(2012, 3, 10)
    date_to_use = datetime.date(2013, 5, 3)
    transfers = parser.get_transfers_on_day(dict_transfers, date_to_use)

    # plot_original_data(transfers, date_to_use, 86400, network_bandwidth=True)
    # plot_modified_data(transfers, date_to_use, 86400, network_bandwidth=True)
    # plot_original_data(transfers, date_to_use, 86400, network_bandwidth=False)
    # plot_modified_data(transfers, date_to_use, 86400, network_bandwidth=False)

    hard_constraint_job_percents = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    make_plot.plot_original_data(transfers, date_to_use, 86400, network_bandwidth=False, plots_folder=plots_folder)
    # make_plot.plot_modified_data(transfers, date_to_use, 86400, network_bandwidth=False, plots_folder=plots_folder,
    #                              non_flexible_jobs_percent=hard_constraint_job_percents)


if __name__ == "__main__":
    main()
