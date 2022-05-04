#! /usr/bin/env python3
#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# power-down.py: AD9548 unit management
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
    parser = argparse.ArgumentParser(description="AD9548 power-down tool")
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
        ('all',  'Complete device power down'),
        ('sysclk', 'Sys clock + pll stage power down'),
        ('ref',  'Ref. input receivers power down'),
        ('dist',  'Distribution stage power down'),
        ('dac',  'DAC power down'),
        ('tdc',  'TDC power down'),
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

    regs = []
    if args.all: # special op
        regs.append((0x0A00, 0x01))
    else:
        if args.sysclk:
            regs.append((0x0A00, 0x20))
        if args.ref:
            regs.append((0x0A00, 0x10))
        if args.dist:
            regs.append((0x0A00, 0x02))
        if args.dac:
            regs.append((0x0A00, 0x04))
        if args.tdc:
            regs.append((0x0A00, 0x08))
        if args.refa:
            regs.append((0x0500, 0x01))
        if args.refaa:
            regs.append((0x0500, 0x02))
        if args.refb:
            regs.append((0x0500, 0x04))
        if args.refbb:
            regs.append((0x0500, 0x08))
        if args.refc:
            regs.append((0x0500, 0x10))
        if args.refcc:
            regs.append((0x0500, 0x20))
        if args.refd:
            regs.append((0x0500, 0x40))
        if args.refdd:
            regs.append((0x0500, 0x80))
    
    for reg in regs: # cli OK
        (addr, mask) = reg
        r = read_data(handle, address, addr)
        if args.clear:
            write_data(handle, address, addr, r & (mask^0xFF)) # mask out
        else:
            write_data(handle, address, addr, r | mask) # assert
        write_data(handle, address, 0x0005, 0x01) # I/O update

if __name__ == "__main__":
    main(sys.argv[1:])
