#! /usr/bin/env python3
#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# irq.py: IRQ event clearing & masking utility
#################################################################
import sys
import argparse
from ad9548 import *
def main (argv):
    parser = argparse.ArgumentParser(description="AD9548 IRQ clearing/masking tool")
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
    parser.add_argument(
        "--pin",
        type=str,
        choices=['nmos','pmos','cmos-high','cmos-low'],
        help="Select output mode of the IRQ pin",
    )
    parser.add_argument(
        "--enable",
        action="store_true",
        help="Enable given IRQ event(s)",
    )
    parser.add_argument(
        "--disable",
        action="store_true",
        help="Disable given IRQ event(s)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear given IRQ event(s)",
    )
    flags = [
        ('all', 'All IRQ flags'),
        ('watchdog', 'Watchdog expiration event'),
        ('dpll', 'All Digital PLL releated events'),
        ('sysclk', 'All Sys clock related events'),
        ('distrib', 'Distribution Sync Event'),
        ('ref', 'All reference sync event'),
        ('history', 'Enables all IRQ for indicating the occurence of tuning word history update'),
        ('freq-unclamped', 'Frequency limiter clamped->unclamped transition event'),
        ('freq-clamped', 'Frequency limiter unclamped->clamped transition event'),
        ('slew-unlimited', 'Phase slew limiter limited->unlimited transition event'),
        ('slew-limited', 'Phase slew limiter unlimited->limited transition event'),
    ]
    for ref in ['a','b','c','d']:
        flags.append(('ref-{}'.format(ref), 'All {} ref. signal related events'.format(ref.upper())))
        flags.append(('ref-{0:}{0:}'.format(ref), 'All {0:}{0:} ref. signal related events'.format(ref.upper())))
    for (ev, helper) in [
        ('switching','DPll switching ref. event'),
        ('closed','DPll closing event'),
        ('freerunning','DPll freerunning event'),
        ('holdover','DPll holdover event'),
        ('freq-unlocked','DPll frequency unlocked event'),
        ('freq-locked','DPll frequency lock event'),
        ('phase-unlocked','DPll phase unlocked event'),
        ('phase-locked','DPll phase lock event')
    ]:
        flags.append(('dpll-{}'.format(ev), helper))
    
    for (ev, helper) in [
        ('unlocked', 'Sys clock unlocking event'),
        ('locked', 'Sys clock locking event'),
        ('cal-complete', 'Sys clock calibration completion event'),
        ('cal-started', 'Sys clock calibration starting event')
    ]:
        flags.append(('sysclk-{}'.format(ev), helper))

    for (ev, helper) in [
        ('fault', 'EEPROM fault event'),
        ('complete', 'EEPROM complete event'),
    ]:
        flags.append(('eeprom-{}'.format(ev), helper))

    for (flag, helper) in flags:
        parser.add_argument(
            "--{}".format(flag), 
            action="store_true",
            help=helper,
        )
    args = parser.parse_args(argv)
    # open device
    dev = AD9548(args.bus, int(args.address,16))

    modes = {
        'nmos': 0,
        'pmos': 1,
        'cmos-high': 2,
        'cmos-low': 3,
    }

    if args.pin:
        # pin special op
        mode = modes[args.pin]
        r = dev.read_data(0x0208)
        dev.write_data(0x0208, r | mode)
        dev.io_update()
        return 0 # terminate

    if args.all:
        if args.clear:
            # clear all: special op
            r = dev.read_data(0x0A03)
            dev.write_data(0x0A03, r | 0x02)
            dev.io_update()
            return 0 # special op
        elif args.enable:
            # enable all: special op
            regs = [
                (0x0209, 0x33),
                (0x020A, 0x0F),
                (0x020B, 0xFF),
                (0x020C, 0x1F),
                (0x020D, 0xFF),
                (0x020E, 0xFF),
                (0x020F, 0xFF),
                (0x0210, 0xFF),
            ]
            for reg in regs:
                (base, mask) = reg
                dev.write_data(base, mask)
            dev.io_update()
            return 0 # special op
        elif args.disable:
            # disable all: special op
            regs = [
                (0x0209, 0x00),
                (0x020A, 0x00),
                (0x020B, 0x00),
                (0x020C, 0x00),
                (0x020D, 0x00),
                (0x020E, 0x00),
                (0x020F, 0x00),
                (0x0210, 0x00),
            ]
            for reg in regs:
                (base, mask) = reg
                dev.write_data(base, mask)
            dev.io_update()
            return 0 # special op
 
    regs = []
    if args.watchdog:
        regs.append(0x020A, 0x04)
    
    if args.dpll:
        regs.append((0x020B, 0xFF))
    if args.dpll_switching:
        regs.append((0x020B, 0x80))
    if args.dpll_closed:
        regs.append((0x020B, 0x40))
    if args.dpll_freerunning:
        regs.append((0x020B, 0x20))
    if args.dpll_holdover:
        regs.append((0x020B, 0x10))
    if args.dpll_freq_unlocked:
        regs.append((0x020B, 0x08))
    if args.dpll_freq_locked:
        regs.append((0x020B, 0x04))
    if args.dpll_phase_unlocked:
        regs.append((0x020B, 0x02))
    if args.dpll_phase_locked:
        regs.append((0x020B, 0x01))

    if args.distrib:
        regs.append((0x020A, 0x08))
    
    if args.sysclk:
        regs.append((0x0209, 0x33))
    if args.sysclk_unlocked:
        regs.append((0x0209, 0x20))
    if args.sysclk_locked:
        regs.append((0x0209, 0x10))
    if args.sysclk_cal_complete:
        regs.append((0x0209, 0x02))
    if args.sysclk_cal_started:
        regs.append((0x0209, 0x01))

    if args.eeprom:
        regs.append((0x020A, 0x03))
    if args.eeprom_fault:
        regs.append((0x020A, 0x02))
    if args.eeprom_complete:
        regs.append((0x020A, 0x01))

    if args.ref:
        # all ref: special opmode'or', 
        regs.append((0x020D, 0xFF))
        regs.append((0x020E, 0xFF))
        regs.append((0x020F, 0xFF))
        regs.append((0x0210, 0xFF))
    if args.refa:
        regs.append((0x020D, 0x0F))
    if args.refaa:
        regs.append((0x020D, 0xF0))
    if args.refb:
        regs.append((0x020E, 0x0F))
    if args.refbb:
        regs.append((0x020E, 0xF0))
    if args.refc:
        regs.append((0x020F, 0x0F))
    if args.refcc:
        regs.append((0x020F, 0xF0))
    if args.refd:
        regs.append((0x0210, 0x0F))
    if args.refdd:
        regs.append((0x0210, 0xF0))

    if args.history:
        regs.append((0x020C, 0x10))
    if args.freq_unclamped:
        regs.append((0x020C, 0x08))
    if args.freq_clamped:
        regs.append((0x020C, 0x04))
    if args.slew_unlimited:
        regs.append((0x020C, 0x02))
    if args.slew_limited:
        regs.append((0x020C, 0x01))

    for reg in regs:
        (addr, mask) = reg # IRQ mask reg
        if args.clear:
            addr += 0x7FB # clear REG offset
        
        r = dev.read_data(addr)
        if args.disable: # clear desired bit(s)
            r &= (mask ^0xFF) # mask out
            dev.write_data(addr, r)
        else: # assert desired bit(s)
            dev.write_data(addr, r | mask)
    dev.io_update()

if __name__ == "__main__":
    main(sys.argv[1:])
