import csv
import collections
import datetime

from copy import deepcopy


columnHeaders = ['id', 'ip_address', 'start_time', 'transfer_time']


def parse_csv(file_name, printer):
    with open(file_name) as file_in:
        reader = csv.reader(file_in)

        header = next(reader)
        rows = []

        bad_rows = 0

        # needed since we use strptime to parse the log entries
        import datetime

        for row in reader:

            if row is None or ''.join(row) is "":
                continue

            column_evals = [
                'int(row[0])',
                'row[1]',
                'datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S.%f")',
                'datetime.datetime.strptime(row[3], "%H:%M:%S.%f")']
            try:

                for idx in range(len(column_evals)):
                    if row[idx] == 'NULL':
                        row[idx] = None
                    else:
                        row[idx] = row[idx].strip()
                        row[idx] = eval(column_evals[idx])
                min_time = datetime.datetime.strptime('0', "%S")
                row[3] = row[3]-min_time
                rows.append(row)
            except Exception:
                print("Could not parse column {} ({}) in this row:".format(idx, columnHeaders[idx]))
                print(row)
                bad_rows += 1
                continue

        if printer is True:
            print("parsed input file: %s" % (file_name))
            print("Parsed %d valid entries." % (len(rows)))
            print("Couldn't parse %d invalid entries" % (bad_rows))

        return header, rows


def dictify_rows(rows):
    dict_rows = []
    for row in rows:
        new_row = {}
        for idx, column in enumerate(row):
            new_row[columnHeaders[idx]] = row[idx]

        # add dict entries to match the globus log entries
        new_row['request_time'] = new_row['start_time']
        new_row['elapsed'] = new_row['transfer_time']

        new_row['complete_time'] = new_row['request_time'] + new_row['elapsed']
        new_row['rate'] = 1
        new_row['bytes'] = int(new_row['rate'] * new_row['elapsed'].total_seconds())

        dict_rows.append(new_row)

    return dict_rows


def get_transfers_by_day(rows, printing):
    transfers_by_day = {}

    for row in rows:
        current_day = row['request_time'].date()
        if current_day in transfers_by_day:
            transfers_by_day[current_day].append(deepcopy(row))
        else:
            transfers_by_day[current_day] = [deepcopy(row)]

        current_day = current_day + datetime.timedelta(days=1)

        while current_day <= row['complete_time'].date():
            if current_day in transfers_by_day:
                transfers_by_day[current_day].append(deepcopy(row))
            else:
                transfers_by_day[current_day] = [deepcopy(row)]

            current_day = current_day + datetime.timedelta(days=1)

    list_of_days = collections.OrderedDict(sorted(transfers_by_day.items()))

    if printing is True:
        for date, transfer_list in list_of_days.items():
            print("%s - %d transfers" % (date, len(transfer_list)))

    return list_of_days


def get_transfers_per_day(rows, printing):
    transfers_per_day = {}

    transfers_by_day = get_transfers_by_day(rows, False)

    for date, transfer_list in transfers_by_day.items():
        count = len(transfer_list)

        if count in transfers_per_day:
            transfers_per_day[count].append(date)
        else:
            transfers_per_day[count] = [date]

    transfers_per_day = collections.OrderedDict(sorted(transfers_per_day.items(),reverse=True))

    if printing is True:
        for count, dates in transfers_per_day.items():
            print("%d transfers/day on %d dates - %s" % (count, len(dates), ', '.join(map(str, dates))))

    return transfers_per_day


# returns a list of the busiest dates
def get_busiest_dates(rows, num_dates):
    transfers_per_day = get_transfers_per_day(rows, False)

    date_list = []
    date_list_count = 0

    for count, dates in transfers_per_day.items():
        for date in dates:
            date_list_count += 1
            date_list.append(date)

            if date_list_count >= num_dates:
                return date_list

    return date_list


# returns a OrderedDict containing the transfer lists for the busiest dates
def get_busiest_days(rows, num_dates, printing):

    date_list = get_busiest_dates(rows, num_dates)

    transfers_by_day = get_transfers_by_day(rows, False)

    top_transfer_days = collections.OrderedDict()

    for date in date_list:
        top_transfer_days[date] = transfers_by_day[date]
        # transfer_list.append(transfers_by_day[date])

    if printing is True:
        print("Daily Transfer Counts for Top {} Days".format(len(date_list)))
        for date, transfer_list in top_transfer_days.items():
            print("%s - %d transfers" % (date, len(transfer_list)))

    return top_transfer_days


# return the date which had the most transfer
def get_max_day(rows, printing):

    transfers_by_day = get_transfers_by_day(rows, False)

    max_date = None
    max_count = 0

    for date, transfer_list in transfers_by_day.items():
        if len(transfer_list) > max_count:
            max_count = len(transfer_list)
            max_date = date

    if printing is True:
        print("Date with the most transfers: %s - (%d transfers)" % (max_date, max_count))

    return max_date, max_count


# returns a list of all the transfers on the given day
def get_transfers_on_day(rows, date):
    transfers_by_day = get_transfers_by_day(rows, False)

    return transfers_by_day[date]


def print_transfers_on_day(rows, date_to_print):
    transfers = get_transfers_on_day(rows, date_to_print)

    # sort by transfer rate descending
    from operator import itemgetter
    transfers = sorted(transfers, key=itemgetter('rate'), reverse=True)

    print("%s - %d transfers" % (date_to_print, len(transfers)))
    for idx, transfer in enumerate(transfers):
        print("%d: %s - %s; Rate: %d; Bytes: %d" % (idx, transfer['request_time'], transfer['complete_time'],
                                                    transfer['rate'], transfer['bytes']))