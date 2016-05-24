import sys
from os.path import isfile

import parse_logs
import make_plot

def main():
    '''Main function'''

    # if len(sys.argv) != 2:
    #     print("Received %d arguments - Expected 1" % (len(sys.argv) - 1))
    #     raise SystemExit
    #
    # file_name = sys.argv[1]

    if len(sys.argv) > 2:
        print("Received %d arguments - Expected 1" % (len(sys.argv) - 1))
        raise SystemExit
    elif len(sys.argv) is 2:
        file_name = sys.argv[1]
    else:
        # file_name = "globus_log.csv"
        file_name = "small_test_globus_log.csv"

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

    max_date, max_count = parse_logs.get_max_day(dict_transfers, True)

    # count = 0
    # for row in dict_transfers:
    #     if row['complete_time'].date() != row['request_time'].date():
    #         if row['request_time'].date() < max_date < row['complete_time'].date():
    #             print("(Start: {}, ---, End: {})".format(row['request_time'], row['complete_time']))
    #             print(row)
    #             print()
    #             count += 1
    # print(count)

    transfers = parse_logs.get_transfers_on_day(dict_transfers, max_date)

    num_bins = 24
    title = "Network Usage on {}".format(max_date)
    plot_filename = "plots/orig_network_demand_{}_{}bins".format(max_date, num_bins)

    make_plot.make_histogram(plot_filename,title, num_bins, transfers, yaxis="linear")

    print(title)
    print(plot_filename)


if __name__ == "__main__":
    main()