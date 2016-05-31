import datetime
import parse_logs
import copy
import csv
import collections


sample_log_entry = collections.OrderedDict(
    [
    ('request_time', datetime.datetime(2000, 1, 1, 0, 0, 0)),
    ('complete_time', datetime.datetime(2000, 1, 1, 0, 0, 0)),
    ('src_logical_name', 'src'),
    ('dst_logical_name', 'dest'),
    ('st_files', 1),
    ('st_faults', 0),
    ('elapsed', datetime.timedelta(0)),
    ('src_name', 'src'),
    ('dst_name', 'dest'),
    ('bytes', 1024*1024),
    ('rate', 0),
    ('src_lat', 1.0),
    ('src_lon', 1.0),
    ('src_city', 'anywhere'),
    ('dst_lat', 2.0),
    ('dst_lon', 2.0),
    ('dst_city', 'anywhere else'),
    ('distance', 100)
    ]
)


# make_triangle_logs('logs/triangle_log.csv', 1000, 0.2, 1000, 5
def make_triangle_log(output_file=None, num_entries=1000, percent_over_lap=0.5,
                      default_transfer_rate=1000, rate_change_multiplier=4, printing=False):

    current_date = datetime.datetime(2000, 1, 1, 0, 0, 0)

    # percent_over_lap = 0.2
    if percent_over_lap < 0.0 or percent_over_lap >= 1.0:
        print('percent_over_lap must be in range [0.0,1) not {}'.format(percent_over_lap))
        return

    transfer_duration = datetime.timedelta(days=1) / (num_entries * (1-percent_over_lap) + percent_over_lap)

    time_between_transfers = transfer_duration * (1-percent_over_lap)

    current_rate = default_transfer_rate

    rate_multiplier = rate_change_multiplier ** (2/num_entries)

    log_entries = []

    for i in range(num_entries):
        cur_entry = copy.copy(sample_log_entry)

        # make entry:
        # set - request_time, complete_time, elapsed, bytes, rate
        cur_entry['request_time'] = current_date + time_between_transfers * i
        cur_entry['elapsed'] = transfer_duration
        cur_entry['complete_time'] = cur_entry['request_time'] + cur_entry['elapsed']

        cur_entry['rate'] = current_rate

        if i < num_entries / 2:
            current_rate *= rate_multiplier
        else:
            current_rate /= rate_multiplier

        cur_entry['bytes'] = round(cur_entry['rate'] * cur_entry['elapsed'].total_seconds())

        log_entries.append(cur_entry)

        if printing is True:
            print('{} - {} -- time: {}, rate: {}, bytes: {}'.
                  format(cur_entry['request_time'], cur_entry['complete_time'],
                         cur_entry['elapsed'], cur_entry['rate'], cur_entry['bytes']))

    # make sure the last entry stays on the correct date even if we trim it a little short
    log_entries[-1]['complete_time'] = min(current_date + datetime.timedelta(days=1) -
                                           datetime.timedelta(microseconds=1), log_entries[-1]['complete_time'])

    if output_file is None:
        output_file = 'logs/triangle_log_{}-entries_{}-overlap.csv'.format(num_entries, percent_over_lap)

    print('Saving log entries to file: {}'.format(output_file))

    csv_file = open(output_file, 'w', newline='\n')

    csv_writer = csv.writer(csv_file)

    csv_writer.writerow(parse_logs.columnHeaders)

    for entry in log_entries:
        entry['elapsed'] = entry['elapsed'].total_seconds()
        entry['request_time'] = entry['request_time'].strftime("%Y-%m-%d %H:%M:%S.%f")
        entry['complete_time'] = entry['complete_time'].strftime("%Y-%m-%d %H:%M:%S.%f")
        cur_list = [value for key, value in entry.items()]
        csv_writer.writerow(cur_list)

    csv_file.close()

