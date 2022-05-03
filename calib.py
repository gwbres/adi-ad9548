#! /usr/bin/env python3
#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# calib.py: calibration script
#################################################################
import sys
import argparse
from smbus import SMBus

def write_data (handle, dev, addr, data):
    msb = (addr & 0xFF00)>>8
    lsb = addr & 0xFF
    handle.write_i2c_block_data(dev, msb, [lsb, data])
def read_data (handle, dev, addr):
    lsb = addr & 0xFF
    msb = (addr & 0xFF00)>>8
    handle.write_i2c_block_data(dev, msb, [lsb])
    data = handle.read_byte(dev)
    return data

def main (argv):
    parser = argparse.ArgumentParser(description="AD9548 calibration tool")
    parser.add_argument(
        "bus",
        help="I2C bus",
    )
    parser.add_argument(
        "address",
        help="I2C slv address",
    )

    # open device
    handle = SMBus()
    handle.open(int(args.bus))
    address = int(args.address, 16)
    r = read_data(handle, address, 0x0A02)
    write_data(handle, address, 0x0A02, r | 0x01) # request cal 
    write_data(handle, address, 0x0005, 0x01) # I/O update

if __name__ == "__main__":
    main(sys.argv[1:])
