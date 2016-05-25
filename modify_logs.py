
import random
import collections


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






