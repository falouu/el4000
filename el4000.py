#!/usr/bin/env python
# Utility to interpret files from the Voltcraft Energy Logger 4000 (as sold by
# Conrad).
#
# Copyright (C) 2014 Peter Wu <peter@lekensteyn.nl>

import os, sys
from argparse import ArgumentParser
import datetime
import logging
from typing import Any, Tuple

from defs import info, data_hdr, data, setup, SETUP_MAGIC, STARTCODE
import printers


ALL_DATA_RAW_FILENAME = "all-data.csv"

_logger = logging.getLogger(__name__)

def process_setup(filename, printer, setup_args):
    # Original setup template, default to empty
    setup_old = None

    try:
        size = os.path.getsize(filename)
        if size != 0 and size != setup.size():
            raise RuntimeError(('Setup file {0} must non-existent, empty or of ' +
                'size {1}, but found {2}').format(filename, setup.size(), size))
        if size == setup.size():
            with open(filename, 'rb') as f:
                setup_old = f.read(size)
                if len(setup_old) != setup.size():
                    _logger.warn('Unable to read setup file')
    except os.error:
        # File does not exist?
        pass
    # If setup file is not initialized, use an empty one
    if not setup_old or len(setup_old) != setup.size():
        setup_old = setup.size() * b'\x00'

    # Unpack old file, ignoring any input errors
    old_t = setup.unpack(setup_old, validate=False)

    if not setup_args:
        # No setup parameters? Just show current values then.
        printers.print_namedtuple(old_t, setup)
    else:
        # Parameters were given. Create mutable dict from old tuples such that
        # the fields can be modified.
        t = dict([(k, v) for k, v in zip(old_t._fields, old_t)])
        for arg in setup_args:
            if not '=' in arg:
                _logger.error('Option %s is missing value, skipping', arg)
                continue

            name, val = arg.split('=', 1)
            if not name in setup.names:
                _logger.error('Invalid setup key: {0}'.format(name))
            else:
                print('Changing {0} from {1} to {2}'.format(name, t[name], val))
                t[name] = float(val)

        # Build new file contents
        setup_new = setup.pack(t)
        new_t = setup.unpack(setup_new, validate=False)

        print('Setup file: ', filename)
        printers.print_namedtuple(new_t, setup)

        # If there are changes, write them away
        if setup_new != setup_old:
            _logger.info('Writing new file')
            with open(filename, 'wb') as f:
                f.write(setup_new)
        else:
            _logger.info('No changes, not writing file')

def process_file(filename, printer, dt, data_only):
    with open(filename, 'rb') as f:
        size = os.fstat(f.fileno()).st_size
        if size == info.size():
            # Info files
            t = info.parse_from_file(f)
            # Initialize time from info file
            dt[0] = datetime.datetime(2000 + t.init_date_year,
                    t.init_date_month, t.init_date_day,
                    t.init_time_hour, t.init_time_minute)
            if not data_only:
                printer.print_info(t)
        else:
            # Data files.

            # First, test whether this file is not a setup file
            buf = f.read(len(SETUP_MAGIC))
            if buf == SETUP_MAGIC:
                _logger.warn('Setup file is ignored. Use --setup option instead')
                return

            eof = 4 * b'\xff'
            while True:
                if len(buf) < len(eof):
                    buf += f.read(len(eof) - len(buf))
                if not buf:
                    break
                elif buf == eof[0:len(buf)]:
                    # End of file code (or short read at the end)
                    #sys.stdout.flush()
                    #_logger.info('EOF detected, skipping')
                    #continue
                    break

                if buf[0:len(STARTCODE)] == STARTCODE:
                    # Not data, but header before data
                    buf += f.read(data_hdr.size() - len(buf))
                    t = data_hdr.unpack(buf)
                    # New time reference!
                    dt[0] = datetime.datetime(2000 + t.record_year,
                            t.record_month, t.record_day,
                            t.record_hour, t.record_minute)
                    printer.print_data_header(t)
                else:
                    buf += f.read(data.size() - len(buf))
                    t = data.unpack(buf)
                    # For time reference
                    date_str = dt[0].strftime('%Y-%m-%d %H:%M')
                    printer.print_data(t, date=date_str)
                    # Assume that this is called for every minute
                    dt[0] += datetime.timedelta(minutes=1)

                # Clear buffer since it is processed
                buf = b''

def run_dir_mode(dir: str, printer):
    _logger.info("Processing dir: %s", dir)

    memory_printer = printers.MemoryPrinter()

    filenames = [] # type: list[str]
    (_, _, filenames) = next(os.walk(dir), (None, None, []))
    if len(filenames) == 0:
        raise Exception("Directory '{}' is empty or invalid".format(dir))


    last_datetime = [None]
    bin_filenames = []
    for filename in filenames:
        if filename.lower().endswith(".bin"):
            bin_filenames.append(filename)
        else:
            _logger.info("Skipping file: %s", filename)

    bin_filenames.sort()

    # first file of files sorted asc by filename treated as HEX number, should be an info file
    # it should initialise last_datetime
    info_filename = bin_filenames[0]
    # apparently bin files, sorted asc are in reversed chrono order. We need to reverse the list
    # and the earliest data file has no header, so last_datetime needs to be initialised before, by reading info file
    data_filenames = reversed(bin_filenames[1:])

    def process_bin_file(filename):
        _logger.info("Processing file: %s", filename)
        abs_path = os.path.join(dir, filename)
        process_file(abs_path, memory_printer, last_datetime, False)

    process_bin_file(info_filename)
    for filename in data_filenames:
        process_bin_file(filename)
    pass

    def verify_sorted(entries):
        last_datetime = "1970-01-01 00:00"
        for entry in entries:
            date = entry["date"]
            if date <= last_datetime:
                raise Exception("Entries are not sorted by date!")
            last_datetime = date
        _logger.info("Entries are correctly sorted by date")

    verify_sorted(memory_printer.data)

    output_info_filepath = os.path.join(dir, "info.yml")
    _logger.info("Writing info to: " + output_info_filepath)
    with open(output_info_filepath, 'x') as output_info_file:
        for entry in memory_printer.info:
            output_info_file.write("{}: {}\n".format(entry["key"], entry["val"]))
    _logger.info("Info written successfully")

    output_data_raw_filepath = os.path.join(dir, ALL_DATA_RAW_FILENAME)
    _logger.info("Writing data to: " + output_data_raw_filepath)
    with open(output_data_raw_filepath, 'x') as output_data_raw_file:
        header = ",".join(["date", "voltage", "current", "power_factor", "apparent_power", "effective_power"])
        output_data_raw_file.write(header + "\n")
        for entry in memory_printer.data:
            line = ",".join([
                entry["date"], 
                str(entry["voltage"]), 
                str(entry["current"]), 
                str(entry["power_factor"]), 
                str(entry["apparent_power"]), 
                str(entry["effective_power"])
            ])
            output_data_raw_file.write(line + "\n")
    _logger.info("Data written successfully")




verbosities = [
    logging.CRITICAL,
    logging.ERROR,
    logging.WARNING, # Default
    logging.INFO,
    logging.DEBUG
]

available_printers = {
    'base': printers.BasePrinter,
    'raw':  printers.RawPrinter,
    'csv':  printers.CSVPrinter,
    'watt': printers.EffectivePowerPrinter,
    'va':   printers.ApparentPowerPrinter
}

parser = ArgumentParser(description='Energy Logger 4000 utility')
parser.add_argument('-p', '--printer', choices=available_printers.keys(),
                    default='base',
                    help="Output formatter (default '%(default)s')")
parser.add_argument('-d', '--delimiter', default=',',
                    help="Output delimiter for CSV output (default '%(default)s')")
parser.add_argument('-v', '--verbose', action='count',
                    default=verbosities.index(logging.WARNING),
                    help='Increase logging level (twice for extra verbose)')
parser.add_argument('-s', '--setup', metavar='key=value', nargs='*',
                    help='Process a setupel3.bin file. Optional parameters \
                    can be given to set a field (-s unit_id=1 for example). \
                    If no parameters are given, the current values are printed')
parser.add_argument('-o', '--data-only', action='store_true',
                    help='Use info files only for updating the initial \
                    timestamp for data files, do not print their contents')
parser.add_argument('files', metavar='binfile', nargs='+',
                    help='info or data files (.bin) from SD card. If --setup \
                    is given, then this is the output file (and input for \
                    defaults). The order of files are significant when a \
                    timestamp is involved')
parser.add_argument('--dir', action='store_true', 
                    help="enable dir mode. Pass one directory - all data will \
                    be saved automatically in chronological order in given directory: data.csv and info")

if __name__ == '__main__':
    args = parser.parse_args()

    # Set log level on root
    args.verbose = min(args.verbose, len(verbosities) - 1)
    logging.basicConfig(level=verbosities[args.verbose])

    myprinter = available_printers[args.printer]
    files_count = len(args.files)
    if args.setup is not None:
        if files_count != 1:
            _logger.error('Only one file can be specified for set-up')
            sys.exit(1)

    # Unknown date and time, initialize with something low.
    dt = [datetime.datetime(1970, 1, 1)]

    if args.dir:
        if files_count != 1:
            _logger.error('Only one file (directory) can be specified for dir mode')
            sys.exit(1)
        run_dir_mode(args.files[0], myprinter)
        sys.exit(0)

    for filename in args.files:
        try:
            printer = myprinter(filename, separator=args.delimiter)
        except TypeError:
            printer = myprinter(filename)
        # Treat setup specially, it acts as input and output file
        if args.setup is not None:
            process_setup(args.files[0], myprinter, args.setup)
        else:
            # Display current filename for multiple files
            if files_count > 1 and not args.data_only:
                print('# ' + filename)

            process_file(filename, printer, dt, args.data_only)
