import csv
import collections
import datetime


columnHeaders = ['request_time', 'complete_time', 'src_logical_name', 'dst_logical_name', 'st_files',
                 'st_faults', 'elapsed', 'src_name', 'dst_name', 'bytes',
                 'rate', 'src_lat', 'src_lon', 'src_city', 'dst_lat',
                 'dst_lon', 'dst_city', 'distance']


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
                'datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")',
                'datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S.%f")',
                'row[2]',
                'row[3]',
                'int(row[4])',
                'int(row[5])',
                'float(row[6])',
                'row[7]',
                'row[8]',
                'int(row[9])',
                'float(row[10])',
                'float(row[11])',
                'float(row[12])',
                'row[13]',
                'float(row[14])',
                'float(row[15])',
                'row[16]',
                'float(row[17])']
            try:

                for idx in range(len(column_evals)):
                    if row[idx] == 'NULL':
                        row[idx] = None
                    else:
                        row[idx] = eval(column_evals[idx])
                rows.append(row)
            except Exception:
                print("couldn't parse this row:")
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
        dict_rows.append(new_row)

    return dict_rows


def get_transfers_by_day(rows, printing):
    transfers_by_day = {}

    for row in rows:
        current_day = row['request_time'].date()
        if current_day in transfers_by_day:
            transfers_by_day[current_day].append(row)
        else:
            transfers_by_day[current_day] = [row]

        current_day = current_day + datetime.timedelta(days=1)

        while current_day <= row['complete_time'].date():
            if current_day in transfers_by_day:
                transfers_by_day[current_day].append(row)
            else:
                transfers_by_day[current_day] = [row]

            current_day = current_day + datetime.timedelta(days=1)

        # if row['complete_time'].date() != row['request_time'].date():
        #     tmp_date = row['request_time'].date()
        #     while tmp_date < row['complete_time'].date():
        #         if current_day in transfers_by_day:
        #             transfers_by_day[current_day].append(row)
        #         else:
        #             transfers_by_day[current_day] = [row]
        #
        #
        #     current_day = row['complete_time'].date()
        #     if current_day in transfers_by_day:
        #         transfers_by_day[current_day].append(row)
        #     else:
        #         transfers_by_day[current_day] = [row]

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

    transfers_per_day = collections.OrderedDict(sorted(transfers_per_day.items()))

    if printing is True:
        for count, dates in transfers_per_day.items():
            print("%d transfers/day on %d dates - %s" % (count, len(dates), ', '.join(map(str, dates))))

    return transfers_per_day


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
