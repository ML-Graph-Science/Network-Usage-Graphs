import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os

plots_parent_dir = "plots/"
plots_dir_orig = os.path.join(plots_parent_dir, os.path.basename(__file__))
plots_dir_orig = plots_dir_orig[:plots_dir_orig.rindex('.')] + '/'
plots_dir = ""

def plot(jobs):
    datetimes = [x[2] for x in jobs]

    time_lengths = []

    prev_item = datetimes[0]
    for item in datetimes:
        time_lengths.append((item - prev_item).total_seconds())
        prev_item = item

    for index, item in enumerate(datetimes):
        print("experiment time: %s -- experiment time length: %s" % (item, time_lengths[index]))

    fig, ax = plt.subplots()

    ax.plot_date(datetimes, time_lengths, xdate=True)
    plt.ylabel('Time between Experiments (Hours:Minutes:Seconds)')
    plt.xlabel('Experiment Time')

    # ax.xaxis.set_major_locator(mpl.dates.HourLocator(interval=6))
    # ax.xaxis.set_minor_locator(mpl.dates.HourLocator())
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%I%p - %m-%d-%Y"))

    def timedelta(x, pos):
        'The two args are the value and tick position'
        hours, remainder = divmod(x, 3600)
        minutes, seconds = divmod(remainder, 60)
        return ('%d:%02d:%02d' % (hours, minutes, seconds))

    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(timedelta))

    fig.autofmt_xdate()
    plt.show()


def make_bar_graph(filename, title, num_bins, transfers, yaxis):

    fig, ax = plt.subplots()

    # logScale = False
    # if yaxis == "log":
    #     logScale = True

    bins = bin_data(num_bins, transfers)

    plt.xlabel('Time of Day')
    plt.ylabel('Network Demand (MiB/S)')
    plt.title(title)

    bytes_in_megabyte = 1024*1024

    x = [cur_bin.start_t for cur_bin in bins]
    y = [cur_bin.bytes for cur_bin in bins]

    # convert bytes to megabytes
    y = [float(val)/bytes_in_megabyte for val in y]

    width = 0.8 / len(bins)

    plt.plot(x, y, color='cornflowerblue', linestyle='-', linewidth=1)
    # plt.bar(x, y, width=width, color='r')

    interval = 3
    xtick_list = [(bins[0].start_t + datetime.timedelta(hours=i*interval)) for i in range(int(24/interval))]
    ax.set_xticks(xtick_list)

    ax.xaxis.set_minor_locator(mpl.dates.HourLocator())
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M:%S'))

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


class Bin(object):
    def __init__(self, start_t, end_t):
        self.start_t = start_t
        self.end_t = end_t
        self.bytes = 0

    def intersect(self, transfer):
        tran_start = transfer['request_time']
        tran_end = transfer['complete_time']

        if (self.start_t <= tran_start <= self.end_t) or (self.start_t <= tran_end <= self.end_t)\
                or (tran_start <= self.start_t and self.end_t <= tran_end):
            return True

        return False

    def __repr__(self):
        return "(start_t: {}, end_t: {}, bytes: {})".format(self.start_t, self.end_t, self.bytes)


# distribute the transfers into the appropriate amount of bins
def bin_data(num_bins, transfers):

    date = transfers[0]['request_time'].date()
    date = datetime.datetime(date.year, date.month, date.day)

    bins = make_bins(num_bins, date)

    for cur_bin in bins:
        for transfer in transfers:

            if cur_bin.intersect(transfer) is True:
                start = max(cur_bin.start_t, transfer['request_time'])
                end = min(cur_bin.end_t, transfer['complete_time'])
                intersect_time = (end - start).total_seconds()
                cur_bin.bytes += round(intersect_time * transfer['rate'])

    return bins


def make_bins(num_bins, date):
    bins = []
    bin_size = 24.0 * 60 * 60 * 1000 * 1000 / num_bins
    for i in range(num_bins):
        microseconds = int(bin_size * i)
        start_t = date + datetime.timedelta(microseconds=microseconds)

        microseconds = int(bin_size * (i+1)) - 1
        end_t = date + datetime.timedelta(microseconds=microseconds)

        cur_bin = Bin(start_t, end_t)
        bins.append(cur_bin)

    return bins
