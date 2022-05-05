#! /usr/bin/env python3
#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# mx-pin.py: programmable I/O management
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
    parser = argparse.ArgumentParser(description="AD9548 mx-pin programmable i/o")
    parser.add_argument(
        "bus",
        help="I2C bus",
    )
    parser.add_argument(
        "address",
        help="I2C slv address",
    )
    io = {
        'input': 0,
        'output': 1,
    }
    macros = {
        'low': {
            'value': 0,
            'helper': 'Static 0 logic level',
        },
        'high': {
            'value': 1,
            'helper': 'Static 1 logic level',
        },
        'sysclk/32': {
            'value': 2,
            'helper': 'Direct sysclock signal /32',
        },
        'watchdog' : {
            'value': 3,
            'helper': 'Watchdog timer output',
        },
        'eeprom-up': {
            'value': 4,
            'helper': 'EEPROM upload in progress',
        },
        'eeprom-down': {
            'value': 5,
            'helper': 'EEPROM download in progress',
        },
        'eeprom-fault': {
            'value': 6,
            'helper': 'EEPROM fault detected',
        },
        'sysclk-pll-lock': {
            'value': 7,
            'helper': 'Sysclk pll lock',
        },
        'sysclk-pll-cal': {
            'value': 8,
            'helper': 'Sysclk pll calibration in progress',
        },
        'sysclk-pll-stable': {
            'value': 11,
            'helper': 'sysclk pll stable',
        },
        'dpll-free-running': {
            'value': 16,
            'helper': 'dpll running',
        },
        'dpll-active': {
            'value': 17,
            'helper': 'dpll active',
        },
        'dpll-holdover': {
            'value': 18,
            'helper': 'dpll holdover',
        },
        'dpll-ref-switchover': {
            'value': 19,
            'helper': 'dpll in reference switchover',
        },
        'active-ref': {
            'value': 20,
            'helper': 'active refenrece: phase master',
        },
        'dpll-phase-locked': {
            'value': 21,
            'helper': 'dpll phase locked',
        },
        'dpll-freq-locked': {
            'value': 22,
            'helper': 'dpll freq locked',
        },
        'dpll-slew-limited': {
            'value': 23,
            'helper': 'dpll phase slew limited',
        },
        'dpll-freq-clamped': {
            'value': 24,
            'helper': 'dpll frequency clamped',
        },
        'history-avail': {
            'value': 25,
            'helper': 'DDS tuning word history is available',
        },
        'history-update': {
            'value': 26,
            'helper': 'DDS tuning word history updated',
        },
        'distrib-sync': {
            'value': 80,
            'helper': 'Clock distribution sync pulse',
        },
    }

    index = 32
    for ref in ['a','aa','b','bb','c','cc','d','dd']:
        macros['ref-{}-fault'.format(ref)] = {
            'value': index,
            'helper': 'Ref {} faulty'.format(ref.upper()),
        }
        macros['ref-{}-valid'.format(ref)] = {
            'value': index+16,
            'helper': 'Ref {} valid'.format(ref.upper()),
        }
        macros['ref-{}-active'.format(ref)] = {
            'value': index+32,
            'helper': 'Ref {} active'.format(ref.upper()),
        }

    parser.add_argument(
        "pin",
        metavar="pin",
        choices=["M0", "M1","M2","M3","M4","M5","M6"],
        help="Select with pin to assign",
        type=str,
    )
    parser.add_argument(
        "io",
        choices=["input","output"],
        help="Select whether this is pin should be set as an input or an output", 
        type=str,
    )
    parser.add_argument(
        "macro",
        metavar="macro",
        choices=list(macros.keys()),
        help="Select special operation to perform with this pin. Available macros: {}".format(str(list(macros.keys()))),
        type=str,
    )
    args = parser.parse_args(argv)

    handle = SMBus()
    handle.open(int(args.bus))
    address = args.address

    pin = args.pin
    pin_n = int(pin.strip("M"))
    io = args.io
    macro = args.macro

    base = 0x0200 + pin_n
    r = io << 7
    r |= macro
    write_data(handle, address, base, r) 
    write_data(handle, address, 0x0005, 0x01) # IO update

if __name__ == "__main__":
    main(sys.argv[1:])
