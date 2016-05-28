
import random
import collections
import datetime


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


def modify_logs(num_bins, transfers, date):
    bins = bin_data(num_bins, transfers, date)

    min_bin_idx, min_bin = get_max_bin(bins)

    max_bin_idx, max_bin = get_max_bin(bins)

    print(min_bin_idx)
    print(min_bin)

    print('')

    print(max_bin_idx)
    print(max_bin)

    print('')

    x_bins, y_bins = split_logs(transfers, 0.5, 0.5)





# distribute the transfers into the appropriate amount of bins
def bin_data(num_bins, transfers, date):

    # turn date object into datetime with time set to all 0
    date = datetime.datetime(date.year, date.month, date.day)

    # make the bins
    bin_size, bins = make_bins(num_bins, date)

    for transfer in transfers:
        # calculate the start and end times for the transfer on the current day
        start_time = max(bins[0].start_t, transfer['request_time'])
        end_time = min(bins[-1].end_t, transfer['complete_time'])

        # calculate the start and end indices of the bins that the transfer intersects with
        start_bin_idx = int((start_time - date).total_seconds() / bin_size)
        end_bin_idx = int((end_time - date).total_seconds() / bin_size)

        # Update the first intersection bin
        intersect_start = max(bins[start_bin_idx].start_t, start_time)
        intersect_end = min(bins[start_bin_idx].end_t, end_time)

        intersect_time = (intersect_end - intersect_start).total_seconds()
        bins[start_bin_idx].bytes += round(intersect_time * transfer['rate'])

        # if the transfer intersects with more than 1 bin
        if start_bin_idx != end_bin_idx:

            num_bytes = round(bin_size * transfer['rate'])
            # Update all of the bins between the first and the last
            for i in range(start_bin_idx+1, end_bin_idx):
                bins[i].bytes += num_bytes

            #  Update the last intersection bin
            intersect_start = max(bins[end_bin_idx].start_t, start_time)
            intersect_end = min(bins[end_bin_idx].end_t, end_time)

            intersect_time = (intersect_end - intersect_start).total_seconds()
            bins[end_bin_idx].bytes += round(intersect_time * transfer['rate'])

    return bins


def make_bins(num_bins, date):
    bins = []
    # calculate bin size in microseconds
    bin_size = 24.0 * 60 * 60 * 1000 * 1000 / num_bins
    for i in range(num_bins):
        microseconds = int(bin_size * i)
        start_t = date + datetime.timedelta(microseconds=microseconds)

        microseconds = int(bin_size * (i+1)) - 1
        end_t = date + datetime.timedelta(microseconds=microseconds)

        cur_bin = Bin(start_t, end_t)
        bins.append(cur_bin)

    # return bin_size in seconds
    return (bin_size / (1000.0 * 1000.0)), bins


def get_min_bin(bins):
    min_bin = bins[0]
    min_bin_idx = 0

    for idx, cur_bin in enumerate(bins):
        if cur_bin.bytes < min_bin.bytes:
            min_bin = cur_bin
            min_bin_idx = idx

    return min_bin_idx, min_bin


def get_max_bin(bins):
    max_bin = bins[0]
    max_bin_idx = 0

    for idx, cur_bin in enumerate(bins):
        if cur_bin.bytes > max_bin.bytes:
            max_bin = cur_bin
            max_bin_idx = idx

    return max_bin_idx, max_bin


def split_logs(transfers, x_percent, y_percent):
    # x_percent + y_percent should = 1
    if x_percent + y_percent != 1:
        print('Error - x_percent({}) + y_percent({}) = {}, but should equal 1'.
              format(x_percent, y_percent, x_percent+y_percent))

    if transfers is None:
        transfers = collections.OrderedDict()
        for i in range(9):
            transfers[i] = "val: {}".format(str(i))

    print(transfers)

    keys = list(transfers.keys())
    random.shuffle(keys)

    shuffled_list = [(key, transfers[key]) for key in keys]

    x_count = round(len(shuffled_list) * x_percent)
    y_count = len(shuffled_list) - x_count

    x_list = shuffled_list[:x_count]
    y_list = shuffled_list[x_count:]

    print(x_list)
    print(y_list)

    x_dict = collections.OrderedDict(x_list)
    y_dict = collections.OrderedDict(y_list)

    print(x_dict)
    print(y_dict)

    return x_dict, y_dict






