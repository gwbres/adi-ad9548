#! /usr/bin/env python3
#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# reset.py: AD9548 device reset utility
#################################################################
import sys
import argparse
from ad9548 import *
def main (argv):
    parser = argparse.ArgumentParser(description="AD9548 reset tool")
    parser.add_argument(
        "bus",
        type=int,
        help="I2C bus (int)",
    )
    parser.add_argument(
        "address",
        type=str,
        help="I2C slv address (hex)",
    )
    flags = [
        ('soft', 'Performs a soft reset but maintains current registers value'),
        ('lf',   'Clears digital loop filter'),
        ('cci',  'Clears cci filter'),
        ('phase','Clears dds phase accumulator'),
        ('autosync','Resets auto sync logic'),
        ('history','Resets tuning word history'),
        ('watchdog','Resets watchdog timer'),
    ]
    for (flag, helper) in flags:
        parser.add_argument(
            "--{}".format(flag), 
            action="store_true",
            help=helper,
        )
    args = parser.parse_args(argv)
    # open device
    dev = AD9548(args.bus, int(args.address,16)) 
    if args.soft:
        reg = dev.read_data(0x0A00)
        dev.write_data(0x0000, reg | 0x01 | 0x80)
        dev.write_data(0x0000, reg)
    if args.watchdog:
        reg = dev.read_data(0x0A03)
        dev.write_data(0x0A03, reg | 0x01)
    if args.lf:
        reg = dev.read_data(0x0A03)
        dev.write_data(0x0A03, reg | 0x40)
    if args.cci:
        reg = dev.read_data(0x0A03)
        dev.write_data(0x0A03, reg | 0x20)
    if args.phase:
        reg = dev.read_data(0x0A03)
        dev.write_data(0x0A03, reg | 0x10)
    if args.autosync:
        reg = dev.read_data(0x0A03)
        dev.write_data(0x0A03, reg | 0x08)
    if args.history:
        reg = dev.read_data(0x0A03)
        dev.write_data(0x0A03, reg | 0x04)
if __name__ == "__main__":
    main(sys.argv[1:])
