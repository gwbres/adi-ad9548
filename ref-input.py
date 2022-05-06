#! /usr/bin/env python3
#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# ref-input.py: AD9548 reference input management
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
    parser = argparse.ArgumentParser(description="AD9548 reference inputs management")
    parser.add_argument(
        "bus",
        help="I2C bus",
    )
    parser.add_argument(
        "address",
        help="I2C slv address",
    )
    flags = [
        ('switching-mode', str, ['automatic','fallback','holdover','manual'],
        """Select the operating mode of the reference switching state machine.
        `automatic` : fully automatic priority based algorithm.
        `fallback` : the active reference is the configured \"user reference\" (--user-ref).
        `holdover` : the active reference is the configured \"user reference\" (--user-ref).
        `manual` :  the active reference is the configured \"user reference\" (--user-ref) 
        which must also be configured for manual reference to profile assignment [profile.py]"""),
        ('logic', str, ['disabled','1.5v-cmos','2.5v-cmos','3.3v-cmos'], """
        Set logic reference level for desired REFx input"""),
    ]
    for (v_flag, v_type, v_choices, v_helper) in flags:
        if v_type is None:
            parser.add_argument(
                "--{}".format(v_flag), 
                action="store_true",
                help=v_helper,
            )
        else:
            parser.add_argument(
                "--{}".format(v_flag), 
                type=v_type,
                choices=v_choices,
                help=v_helper,
            )
    parser.add_argument(
        '--ref',
        choices=['a','aa','b','bb','c','cc','d','dd','all'],
        default="all",
        help="""Select desired input reference. 
        Defaults to `all`. Aux-x means auxilary-x input reference, when feasible.""",
    )
    args = parser.parse_args(argv)

    pin = args.pin
    ref = args.ref

    # open device
    handle = SMBus()
    handle.open(int(args.bus))
    address = int(args.address, 16)

    logics = {
        'disabled':  0,
        '1.5v-cmos': 1,
        '2.5v-cmos': 2,
        '3.3v-cmos': 3,
    }

    if args.logic:
        if args.ref == "all":
            mask = logics[args.logic]
            mask |= logics[args.logic] << 2
            mask |= logics[args.logic] << 4
            mask |= logics[args.logic] << 6
            write_data(handle, address, 0x0501, mask) # assign all
            write_data(handle, address, 0x0502, mask) # assign all
        else:
            mask = logics[args.logic] 
            if (args.ref == "aa") or (args.ref == "cc"):
                mask = mask << 2
            if (args.ref == "b") or (args.ref == "d"):
                mask = mask << 4
            if (args.ref == "bb") or (args.ref == "dd"):
                mask = mask << 6
            if ((args.ref == "c") or  (args.ref == "cc") or (args.ref == "d") or (args.ref == "dd")):
                addr = 0x0502
            else:
                addr = 0x0501
            r = read_data(handle, address, addr)
            r &= (mask ^0xFF) # clear bit(s)
            write_data(handle, address, addr, r|mask) # assign bit(s)

    write_data(handle, address, 0x000F, 0x01) # i/o update

if __name__ == "__main__":
    main(sys.argv[1:])
