import copy
import random
import datetime
from operator import itemgetter
import numpy
import bisect

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


def assign_max_prices(original_bins, transfers, min_range, max_range):

    min_bin_idx, min_bin = get_min_bin(original_bins)
    max_bin_idx, max_bin = get_max_bin(original_bins)

    min_value = (max_bin.bytes - min_bin.bytes) * min_range + min_bin.bytes
    max_value = (max_bin.bytes - min_bin.bytes) * max_range + min_bin.bytes

    # uniform distribution max_prices
    # for transfer in y_transfers:
    #     value = random.uniform(min_value, max_value)
    #     transfer['max_price'] = value

    # # exponential distribution max_prices
    # for transfer in y_transfers:
    #     value = min_value + (max_value - min_value) * 0.5 * random.expovariate(1)
    #     transfer['max_price'] = value

    bin_values = [cur_bin.bytes for cur_bin in original_bins]
    bin_values.sort()

    # remove the top 5% of values from the list
    bin_values[:int(len(bin_values) * 0.95)]

    mean_value = numpy.mean(bin_values)
    std_deviation = numpy.std(bin_values)
    median_value = numpy.median(bin_values)

    print("\nmin bin value: {}, max bin value: {}".format(min_bin.bytes, max_bin.bytes))
    print("min range value: {}, max range value: {}".format(min_value, max_value))
    print("median bin value: {}, std deviation: {}".format(median_value, std_deviation))
    print("average bin value: {}".format(mean_value))

    # normal distribution max_prices
    for transfer in transfers:
        cur_value = random.gauss(mean_value, std_deviation)
        while cur_value < min_value or max_value < cur_value:
            cur_value = random.gauss(mean_value, std_deviation)
        transfer['max_price'] = cur_value

    # max_prices = [transfer['max_price'] for transfer in transfers]
    # print("\nMax Prices for Y Transfers")
    # print(max_prices)

#
# def splits_logs_and_bin_data(num_bins, transfers, date, x_percent, network_bandwidth):
#
#     x_transfers, y_transfers = split_logs(transfers, x_percent, 1 - x_percent)
#
#     # if network_bandwidth is True then bin the data using the bin_data_using_transfer_rates function
#     if network_bandwidth is True:
#         x_bins = bin_data_using_transfer_rates(None, num_bins, x_transfers, date)
#         new_bins = bin_data_using_transfer_rates(x_bins, len(x_bins), y_transfers, date)
#     # else if it is False, then bin the data using the bin_data_using_concurrent_transfers function
#     else:
#         x_bins = bin_data_using_concurrent_transfers(None, num_bins, x_transfers, date)
#         new_bins = bin_data_using_concurrent_transfers(x_bins, len(x_bins), y_transfers, date)
#
#     return x_bins, new_bins
#
#
# def split_logs_and_modify_transfers(num_bins, transfers, date, min_range, max_range, x_percent, network_bandwidth):
#
#     # if network_bandwidth is True then bin the data using the bin_data_using_transfer_rates function
#     if network_bandwidth is True:
#         bins = bin_data_using_transfer_rates(None, num_bins, transfers, date)
#     # else if it is False, then bin the data using the bin_data_using_concurrent_transfers function
#     else:
#         bins = bin_data_using_concurrent_transfers(None, num_bins, transfers, date)
#
#     x_transfers, y_transfers = split_logs(transfers, x_percent, 1-x_percent)
#
#     # if network_bandwidth is True then bin the data using the bin_data_using_transfer_rates function
#     if network_bandwidth is True:
#         x_bins = bin_data_using_transfer_rates(None, num_bins, x_transfers, date)
#     # else if it is False, then bin the data using the bin_data_using_concurrent_transfers function
#     else:
#         x_bins = bin_data_using_concurrent_transfers(None, num_bins, x_transfers, date)
#
#     min_bin_idx, min_bin = get_min_bin(bins)
#     max_bin_idx, max_bin = get_max_bin(bins)
#
#     min_value = (max_bin.bytes - min_bin.bytes) * min_range + min_bin.bytes
#     max_value = (max_bin.bytes - min_bin.bytes) * max_range + min_bin.bytes
#
#     # uniform distribution max_prices
#     # for transfer in y_transfers:
#     #     value = random.uniform(min_value, max_value)
#     #     transfer['max_price'] = value
#
#     # # exponential distribution max_prices
#     # for transfer in y_transfers:
#     #     value = min_value + (max_value - min_value) * 0.5 * random.expovariate(1)
#     #     transfer['max_price'] = value
#
#     bin_values = [cur_bin.bytes for cur_bin in bins]
#     bin_values.sort()
#
#     # remove the top 5% of values from the list
#     bin_values[:int(len(bin_values) * 0.95)]
#
#     mean_value = numpy.mean(bin_values)
#     std_deviation = numpy.std(bin_values)
#     median_value = numpy.median(bin_values)
#
#     print("\nmin bin value: {}, max bin value: {}".format(min_bin.bytes, max_bin.bytes))
#     print("min range value: {}, max range value: {}".format(min_value, max_value))
#     print("median bin value: {}, std deviation: {}".format(median_value, std_deviation))
#     print("average bin value: {}".format(mean_value))
#
#     # normal distribution max_prices
#     for transfer in y_transfers:
#         cur_value = random.gauss(mean_value, std_deviation)
#         while cur_value < min_value or max_value < cur_value:
#             cur_value = random.gauss(mean_value, std_deviation)
#         transfer['max_price'] = cur_value
#
#     max_prices = [transfer['max_price'] for transfer in y_transfers]
#     # print("\nMax Prices for Y Transfers")
#     # print(max_prices)
#
#     # if network_bandwidth is True then bin the data using the bin_data_using_transfer_rates function
#     if network_bandwidth is True:
#         new_bins = bin_data_using_transfer_rates(x_bins, len(x_bins), y_transfers, date)
#     # else if it is False, then bin the data using the bin_data_using_concurrent_transfers function
#     else:
#         new_bins = bin_data_using_concurrent_transfers(x_bins, len(x_bins), y_transfers, date)
#
#     return bins, x_bins, new_bins


#
#  I still need to update the transfer_rates code to reflect corrections I made for concurrent transfer function
#
# # distribute the transfers into the appropriate amount of bins
# # bin data using the transfer rates and so each bin has the sum of the data transferred during its interval
# def bin_data_using_transfer_rates(old_bins, num_bins, transfers, date, max_prices=False):
#     # turn date object into datetime with time set to all 0
#     date_time = datetime.datetime(date.year, date.month, date.day)
#
#     if old_bins is None:
#         # make the bins
#         bin_size, bins = make_bins(num_bins, date_time)
#
#     else:
#         # get the bin_size
#         bin_size = (old_bins[1].start_t - old_bins[0].start_t).total_seconds()
#         bins = copy.deepcopy(old_bins)
#
#     for transfer in transfers:
#
#         # calculate the start and end times for the transfer on the current day
#         start_time = max(bins[0].start_t, transfer['request_time'])
#         end_time = min(bins[-1].end_t, transfer['complete_time'])
#
#         # calculate the start and end indices of the bins that the transfer intersects with
#         start_bin_idx = int((start_time - date_time).total_seconds() / bin_size)
#         end_bin_idx = int((end_time - date_time).total_seconds() / bin_size)
#
#         # if the transfer has been designated as non-critical, assigned a max price,
#         # and the current start_time exceeds that price, then find the soonest start_time that fits that price
#
#         tmp_val = bins[start_bin_idx].bytes
#         if 'max_price' in transfer:
#             tmp_val2 = transfer['max_price']
#
#         if max_prices is True and 'max_price' in transfer and bins[start_bin_idx].bytes > transfer['max_price']:
#
#             while start_bin_idx < num_bins and bins[start_bin_idx].bytes > transfer['max_price']:
#                 start_bin_idx += 1
#
#             if start_bin_idx >= num_bins:
#                 print('\nUnable to start transfer on day for price reasons \n{}'.format(transfer))
#                 continue
#
#             # calculate the new start and end time for the job
#             start_time = bins[start_bin_idx].start_t
#             end_time = min(bins[-1].end_t, start_time + transfer['elapsed'])
#
#             # check if the transfer is being trimmed
#             # if end_time - start_time < transfer['elapsed']:
#             #     print('\nunable to finish transfer on day for price reasons \n{}'.format(transfer))
#
#             # calculate the new shifted end_bin_idx
#             end_bin_idx = int((end_time - date_time).total_seconds() / bin_size)
#
#         # Update the first intersection bin
#         intersect_start = max(bins[start_bin_idx].start_t, start_time)
#         intersect_end = min(bins[start_bin_idx].end_t + datetime.timedelta(microseconds=1), end_time)
#
#         intersect_time = (intersect_end - intersect_start).total_seconds()
#         bins[start_bin_idx].bytes += round(intersect_time * transfer['rate'])
#
#         # if the transfer intersects with more than 1 bin
#         if start_bin_idx != end_bin_idx:
#
#             num_bytes = round(bin_size * transfer['rate'])
#             # Update all of the bins between the first and the last
#             for i in range(start_bin_idx + 1, end_bin_idx):
#                 bins[i].bytes += num_bytes
#
#             # Update the last intersection bin
#             intersect_start = max(bins[end_bin_idx].start_t, start_time)
#             intersect_end = min(bins[end_bin_idx].end_t + datetime.timedelta(microseconds=1), end_time)
#
#             intersect_time = (intersect_end - intersect_start).total_seconds()
#             bins[end_bin_idx].bytes += round(intersect_time * transfer['rate'])
#
#     return bins


# distribute the transfers into the appropriate amount of bins
# bin data ignoring the transfer rates
# so each bin's value is simply the number of concurrent transfers during its interval
def bin_data_using_concurrent_transfers(old_bins, num_bins, transfers, date, max_prices=False):
    # turn date object into datetime with time set to all 0
    date_time = datetime.datetime(date.year, date.month, date.day)

    if old_bins is None:
        # make the bins
        bin_size, bins_prev_day = make_bins(num_bins, date_time - datetime.timedelta(days=1))
        bin_size, bins_cur_day = make_bins(num_bins, date_time)
        bins = bins_prev_day + bins_cur_day

    else:
        # get the bin_size
        bin_size = (old_bins[1].start_t - old_bins[0].start_t).total_seconds()
        bins = copy.deepcopy(old_bins)

    not_queued_transfers = sorted(transfers, key=itemgetter('request_time'))
    queued_transfers = []
    queued_max_prices_list = []

    current_price = -1

    if max_prices is False:
        for idx, cur_bin in enumerate(bins):
            while len(not_queued_transfers) > 0 and not_queued_transfers[0]['request_time'] <= cur_bin.end_t:
                tran = not_queued_transfers.pop(0)
                end_bin_idx = min(idx + int(numpy.ceil(tran['elapsed'].total_seconds() / bin_size)), len(bins) - 1)
                for i in range(idx, end_bin_idx + 1):
                    bins[i].bytes += 1

    elif max_prices is True:

        for idx, cur_bin in enumerate(bins):

            if cur_bin.start_t.date() == date and cur_bin.start_t.time() == datetime.time(hour=21):
                pass

            old_price = current_price
            current_price = cur_bin.bytes
            while len(not_queued_transfers) > 0 and not_queued_transfers[0]['request_time'] <= cur_bin.end_t:
                transfer_to_queue = not_queued_transfers.pop(0)
                insert_idx = bisect.bisect(queued_max_prices_list, transfer_to_queue['max_price'])
                queued_transfers.insert(insert_idx, transfer_to_queue)
                queued_max_prices_list.insert(insert_idx, transfer_to_queue['max_price'])

                if transfer_to_queue['max_price'] >= current_price:
                    old_price = -1

            if len(queued_transfers) == 0 or current_price == old_price:
                continue

            while True:
                current_price = cur_bin.bytes
                bisect_index = bisect.bisect_left(queued_max_prices_list, current_price)
                valid_queued_transfers = queued_transfers[bisect_index:]

                if len(valid_queued_transfers) == 0:
                    break

                tran = min(valid_queued_transfers, key=itemgetter('request_time'))

                end_bin_idx = min(idx + int(numpy.ceil(tran['elapsed'].total_seconds() / bin_size)), len(bins) - 1)
                for i in range(idx, end_bin_idx + 1):
                    bins[i].bytes += 1

                tran_index = queued_transfers.index(tran)

                del queued_transfers[tran_index]
                del queued_max_prices_list[tran_index]

        print("\nTransfers left in queued_transfers: {}".format(len(queued_transfers)))
        # for tran in queued_transfers:
        #     print("({} - {}) [{} seconds] - max_price: {}".format(tran['request_time'], tran['complete_time'],
        #                                                           tran['elapsed'].total_seconds(),
        #                                                           tran['max_price']))

    # for transfer in transfers:
    #
    #     # calculate the start and end times for the transfer on the current day
    #     start_time = max(bins[0].start_t, transfer['request_time'])
    #     end_time = min(bins[-1].end_t, transfer['complete_time'])
    #
    #     # calculate the start and end indices of the bins that the transfer intersects with
    #     start_bin_idx = int((start_time - date_time).total_seconds() / bin_size)
    #     end_bin_idx = int((end_time - date_time).total_seconds() / bin_size)
    #
    #     # if the transfer has been designated as non-critical, assigned a max price,
    #     # and the current start_time exceeds that price, then find the soonest start_time that fits that price
    #
    #     tmp_val = bins[start_bin_idx].bytes
    #     if 'max_price' in transfer:
    #         tmp_val2 = transfer['max_price']
    #
    #     if max_prices is True and 'max_price' in transfer and bins[start_bin_idx].bytes > transfer['max_price']:
    #
    #         while start_bin_idx < num_bins and bins[start_bin_idx].bytes > transfer['max_price']:
    #             start_bin_idx += 1
    #
    #         if start_bin_idx >= num_bins:
    #             print('\nUnable to start transfer on day for price reasons \n{}'.format(transfer))
    #             continue
    #
    #         # calculate the new start and end time for the job
    #         start_time = bins[start_bin_idx].start_t
    #         end_time = min(bins[-1].end_t, start_time + transfer['elapsed'])
    #
    #         # check if the transfer is being trimmed
    #         # if end_time - start_time < transfer['elapsed']:
    #         #     print('\nunable to finish transfer on day for price reasons \n{}'.format(transfer))
    #
    #         # calculate the new shifted end_bin_idx
    #         end_bin_idx = int((end_time - date_time).total_seconds() / bin_size)
    #
    #     # add the transfer to all of the intersecting bins
    #     for i in range(start_bin_idx, end_bin_idx+1):
    #         bins[i].bytes += 1

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

#
# def split_logs(transfers, x_percent, y_percent):
#     # x_percent + y_percent should = 1
#     if x_percent + y_percent != 1:
#         print('Error - x_percent({}) + y_percent({}) = {}, but should equal 1'.
#               format(x_percent, y_percent, x_percent+y_percent))
#
#     shuffled_list = list(transfers)
#     random.shuffle(shuffled_list)
#
#     x_count = round(len(shuffled_list) * x_percent)
#
#     x_list = shuffled_list[:x_count]
#     y_list = shuffled_list[x_count:]
#
#     # need to sort the lists by transfer request time
#     x_list = sorted(x_list, key=itemgetter('request_time'))
#     y_list = sorted(y_list, key=itemgetter('request_time'))
#
#     return x_list, y_list






