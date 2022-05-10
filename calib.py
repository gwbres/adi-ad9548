#! /usr/bin/env python3
#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# calib.py: AD9548 calibration script
#################################################################
import sys
import argparse
from ad9548 import *
def main (argv):
    parser = argparse.ArgumentParser(description="AD9548 calibration tool")
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
    args = parser.parse_args(argv)
    # open device
    dev = AD9548(args.bus, int(args.address, 16))
    r = read_data(handle, address, 0x0A02)
    write_data(handle, address, 0x0A02, r | 0x01) # request cal 
    dev.io_update()
    write_data(handle, address, 0x0A02, r & (0x01^0xFF)) # and clear
    dev.io_update()

if __name__ == "__main__":
    main(sys.argv[1:])
