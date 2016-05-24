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

    ax.set_xscale(xaxis)

    plt.xlabel('Time of Day')
    plt.ylabel('Network Demand (Bytes)')

    plt.title(title)

    def timedelta(x, pos):
        'The two args are the value and tick position'
        hours, remainder = divmod(x, 3600)
        minutes, seconds = divmod(remainder, 60)
        return ('%d:%02d:%02d' % (hours, minutes, seconds))

    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(timedelta))

    fig.autofmt_xdate()

    # if header is not None:
    #     fn = header['file']
    #     save_file_name = fn[(fn.rindex('/')+1):fn.rindex('.')] + ".png"
    # else:
    #     save_file_name = "all.png"
    # save_file_name = os.path.join(plots_dir, save_file_name)

    print("\nSaving plot to %s" % filename)

    fig.subplots_adjust(left=0.2, bottom=0.25)
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
        # tran_end = tran_start + datetime.timedelta(seconds=transfer['elapsed'])

        if (self.start_t <= tran_start <= self.end_t) or (self.start_t <= tran_end <= self.end_t)\
                or (tran_start <= self.start_t and self.end_t <= tran_end):
            # print(transfer)
            # print('    intersects with bin: {}'.format(self))
            # start = max(self.start_t, tran_start)
            # end = min(self.end_t, tran_end)
            # print('----(start time: {}, end time: {})'.format(start, end))
            # print(intersect_time)

            return True

        return False

        # if (tran_start >= self.start_t and tran_start <= self.end_t) \
        #         or tran_end <= self.end_t:
        #     print(transfer)
        #     print('    intersects with bin: {}'.format(self))

    def __repr__(self):
        return "(start_t: {}, end_t: {}, bytes: {})".format(self.start_t, self.end_t, self.bytes)


# distribute the transfers into the appropriate amount of bins
def bin_data(num_bins, transfers):

    date = transfers[0]['request_time'].date()
    date = datetime.datetime(date.year, date.month, date.day)
    bins = make_bins(num_bins, date)

    for cur_bin in bins:
        for transfer in transfers:
            # time = transfer['request_time']
            # bytes = transfer['bytes']
            # transfer_time = transfer['elapsed']
            # rate = transfer['rate']

            if cur_bin.intersect(transfer) is True:
                # print(transfer)
                # tran_start = transfer['request_time']
                # tran_end = transfer['complete_time']
                start = max(cur_bin.start_t, transfer['request_time'])
                end = min(cur_bin.end_t, transfer['complete_time'])
                intersect_time = (end - start).total_seconds()

                intersect_bytes = round(intersect_time * transfer['rate'])

                print("Transfer: (start - {}), (end - {})".format(transfer['request_time'], transfer['complete_time']))
                print('    intersects with bin: {} ----(start time: {}, end time: {}) --- bytes: {}'.format(cur_bin, start, end, intersect_bytes))
                print('        seconds: {} --- rate: {} --- bytes: {}'.format(intersect_time, transfer['rate'], intersect_bytes))

                cur_bin.bytes += intersect_time * transfer['rate']

                # print('----(start time: {}, end time: {})'.format(start, end))


    # for transfer in transfers:
    #     time = transfer['request_time']
    #     bytes = transfer['bytes']
    #     transfer_time = transfer['elapsed']
    #     rate = transfer['rate']
    #     while bytes > 0:
    #         get_bin(bins, time)


# def make_bins(num_bins, date):
#     bins = []
#     bin_size = 24.0 * 60 * 60 / num_bins
#     print(bin_size)
#     for i in range(num_bins):
#         seconds = int(bin_size * i)
#         m, s = divmod(seconds, 60)
#         h, m = divmod(m, 60)
#         d, h = divmod(h, 24)
#         start_t = date + datetime.timedelta(hours=h, minutes=m, seconds=s)
#         # start_t = datetime.time(h, m, s)
#         seconds = int(bin_size * (i+1)) - 1
#         m, s = divmod(seconds, 60)
#         h, m = divmod(m, 60)
#         d, h = divmod(h, 24)
#         end_t = date + datetime.timedelta(hours=h, minutes=m, seconds=s)
#         # end_t = datetime.time(h, m, s)
#         # bin = {'start_time': start_t, 'end_time': end_t, 'bytes': 0}
#         # bins.append((start_t, end_t, 0))
#
#         cur_bin = Bin(start_t, end_t)
#         bins.append(cur_bin)
#
#     print(bins)
#
#     return bins


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
