#! /usr/bin/env python3
#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# power-down.py
# small script to perform power down operations
# Any power down will probably require either a partial
# or a complete recalibration
#################################################################
import sys
import argparse
from smbus import SMBus

def write_data (handle, dev, addr, data):
    msb = (addr & 0xFF00)>>8
    lsb = addr & 0xFF
    handle.write_i2c_block_data(dev, msb, [lsb, data])
def read_data (handle, dev, addr):
    msb = (addr & 0xFF00)>>8
    lsb = addr & 0xFF
    handle.write_i2c_block_data(dev, msb, [lsb])
    data = handle.read_byte(dev)
    return data

def main (argv):
    parser = argparse.ArgumentParser(description="AD9547/48 power-down tool")
    parser.add_argument(
        "bus",
        help="I2C bus",
    )
    parser.add_argument(
        "address",
        help="I2C slv address",
    )
    flags = [
        ('clear', 'Clear (recover from a previous) power down op'), 
        ('all',   'Device power down (Sys clock pll, REFx, DPlls, APlls..)'),
        ('refa',  'ref-a input receiver power down'),
        ('refaa',  'ref-aa input receiver power down'),
        ('refb',  'ref-b input receiver power down'),
        ('refbb',  'ref-bb input receiver power down'),
        ('refc',  'ref-c input receiver power down'),
        ('refcc',  'ref-cc input receiver power down'),
        ('refd',  'ref-d input receiver power down'),
        ('refdd',  'ref-dd input receiver power down'),
    ]
    for (flag, helper) in flags:
        parser.add_argument(
            "--{}".format(flag), 
            action="store_true",
            help=helper,
        )
    args = parser.parse_args(argv)

    # open device
    handle = SMBus()
    handle.open(int(args.bus))
    address = int(args.address, 16)

    reg = read_data(handle, address, 0x0500)
    if args.all:
        if args.clear:
            reg &= 0x00
        else:
            reg |= 0xFF
    else:
        if args.refa:
            if args.clear:
                reg &= 0xFE
            else:
                reg |= 0x01
        if args.refaa:
            if args.clear:
                reg &= 0xFD
            else:
                reg |= 0x02
        if args.refb:
            if args.clear:
                reg &= 0xFB
            else:
                reg |= 0x04
        if args.refbb:
            if args.clear:
                reg &= 0xF7
            else:
                reg |= 0x08
        if args.refc:
            if args.clear:
                reg &= 0xEF
            else:
                reg |= 0x10
        if args.refcc:
            if args.clear:
                reg &= 0xDF
            else:
                reg |= 0x20
        if args.refd:
            if args.clear:
                reg &= 0xBF
            else:
                reg |= 0x40
        if args.refdd:
            if args.clear:
                reg &= 0x7F
            else:
                reg |= 0x80
    write_data(handle, address, 0x0500, reg)
    write_data(handle, address, 0x000F, 0x01) # I/O update

if __name__ == "__main__":
    main(sys.argv[1:])
