#! /usr/bin/env python3
#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# reset.py: reset AD9548,47 device
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
    parser = argparse.ArgumentParser(description="AD9548/47 reset tool")
    parser.add_argument(
        "bus",
        help="I2C bus",
    )
    parser.add_argument(
        "address",
        help="I2C slv address",
    )
    flags = [
        ('soft', 'Performs a soft reset but maintains current registers value'),
        ('irq',  'Resets all IRQs'),
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
    handle = SMBus()
    handle.open(int(args.bus))
    address = int(args.address, 16)

    if args.soft:
        reg = read_data(handle, address, 0x0A00)
        reg &= 0x7E # clear bits
        write_data(handle, address, 0x0000, reg | 0x01 | 0x80)
        write_data(handle, address, 0x0000, reg)
    if args.irq:
        reg = read_data(handle, address, 0x0A03)
        reg &= 0xFD
        write_data(handle, addresss, 0x0A03, r | 0x02)
    if args.watchdog:
        reg = read_data(handle, address, 0x0A03)
        reg &= 0xFE
        write_data(handle, addresss, 0x0A03, reg | 0x01)
    if args.lf:
        reg = read_data(handle, address, 0x0A03)
        reg &= 0xBF
        write_data(handle, addresss, 0x0A03, reg | 0x40)
    if args.cci:
        reg = read_data(handle, address, 0x0A03)
        reg &= 0xDF
        write_data(handle, addresss, 0x0A03, reg | 0x20)
    if args.phase:
        reg = read_data(handle, address, 0x0A03)
        reg &= 0xEF
        write_data(handle, addresss, 0x0A03, reg | 0x10)
    if args.autosync:
        reg = read_data(handle, address, 0x0A03)
        reg &= 0xF7
        write_data(handle, addresss, 0x0A03, reg | 0x08)
    if args.history:
        reg = read_data(handle, address, 0x0A03)
        reg &= 0xFB
        write_data(handle, addresss, 0x0A03, reg | 0x04)
if __name__ == "__main__":
    main(sys.argv[1:])
