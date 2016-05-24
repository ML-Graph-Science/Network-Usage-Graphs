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


def make_histogram(filename, title, num_bins, transfers, yaxis):

    fig, ax = plt.subplots()

    # logScale = False
    # if yaxis == "log":
    #     logScale = True
    #
    # ax.hist(time_lengths, bins=bins, log=logScale)

    bins = bin_data(num_bins, transfers)

    for cur_bin in bins:
        print(cur_bin)

    # ax.set_xscale(xaxis)

    plt.xlabel('Time of Day')
    plt.ylabel('Network Demand (Bytes)')
    plt.title(title)

    # x = [t.hour * 3600 + t.minute * 60 + t.second for t in [cur_bin.start_t.time() for cur_bin in bins]]

    seconds_per_hour = 60*60
    x = [cur_bin.start_t for cur_bin in bins]
    y = [cur_bin.bytes for cur_bin in bins]

    width = 0.2

    # plt.plot_date(x, y, fmt='bo', xdate=True)

    plt.bar(x, y, width=0.9/len(bins), color='r')

    def timedelta(x, pos):
        'The two args are the value and tick position'
        hours, remainder = divmod(x, 3600)
        minutes, seconds = divmod(remainder, 60)
        return ('%d:%02d:%02d' % (hours, minutes, seconds))

    # ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(timedelta))

    # ax.xaxis.set_major_locator(mpl.dates.HourLocator(interval=3))

    xtick_interval = 3
    ax.set_xticks([cur_bin.start_t for cur_bin in bins[0::xtick_interval]])

    ax.xaxis.set_minor_locator(mpl.dates.HourLocator())
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M:%S'))

    datemin = bins[0].start_t - datetime.timedelta(hours=1)
    datemax = bins[-1].end_t + datetime.timedelta(hours=1)
    ax.set_xlim(datemin, datemax)

    fig.autofmt_xdate()

    # ax.xaxis_date()

    # if header is not None:
    #     fn = header['file']
    #     save_file_name = fn[(fn.rindex('/')+1):fn.rindex('.')] + ".png"
    # else:
    #     save_file_name = "all.png"
    # save_file_name = os.path.join(plots_dir, save_file_name)

    print("\nSaving plot to %s" % filename)

    # fig.subplots_adjust(left=0.2, bottom=0.25)
    plt.savefig(filename, dpi=500)

    plt.close(fig)


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
    print(bin_size)
    for i in range(num_bins):
        microseconds = int(bin_size * i)
        start_t = date + datetime.timedelta(microseconds=microseconds)

        microseconds = int(bin_size * (i+1)) - 1
        end_t = date + datetime.timedelta(microseconds=microseconds)

        cur_bin = Bin(start_t, end_t)
        bins.append(cur_bin)

    print(bins)

    return bins
