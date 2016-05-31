import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import os


def make_line_plot(filename, title, bins, new_bins=None, x_bins=None):

    fig, ax = plt.subplots()

    plt.xlabel('Time of Day')
    plt.ylabel('Network Demand (MiB/S)')
    plt.title(title)

    bytes_in_megabyte = 1024*1024

    x = [cur_bin.start_t for cur_bin in bins]
    y = [cur_bin.bytes for cur_bin in bins]

    # convert bytes to megabytes
    y = [float(val)/bytes_in_megabyte for val in y]

    plt.plot(x, y, color='cornflowerblue', linestyle='-', linewidth=0.5, label='Transfers')

    if new_bins is not None:
        x = [cur_bin.start_t for cur_bin in new_bins]
        y = [cur_bin.bytes for cur_bin in new_bins]

        # convert bytes to megabytes
        y = [float(val) / bytes_in_megabyte for val in y]
        plt.plot(x, y, color='red', linestyle='-', linewidth=0.5, label='Modified Transfers')

    if x_bins is not None:
        x = [cur_bin.start_t for cur_bin in x_bins]
        y = [cur_bin.bytes for cur_bin in x_bins]

        # convert bytes to megabytes
        y = [float(val) / bytes_in_megabyte for val in y]
        plt.plot(x, y, color='green', linestyle='-', linewidth=0.5, label='X Transfers')

    if new_bins is not None and x_bins is not None:
        plt.legend(loc=9, bbox_to_anchor=(0.5, -0.1), ncol=3, borderaxespad=1.7)

    elif new_bins is not None or x_bins is not None:
        plt.legend(loc=9, bbox_to_anchor=(0.5, -0.1), ncol=2, borderaxespad=1.7)

    interval = 3
    xtick_list = [(bins[0].start_t + datetime.timedelta(hours=i*interval)) for i in range(int(24/interval))]
    ax.set_xticks(xtick_list)

    ax.xaxis.set_minor_locator(mpl.dates.HourLocator())
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))

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

