#! /usr/bin/env python3
#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# distrib.py: AD9548 clock distribution management
#################################################################
import sys
import math
import argparse
from ad9548 import *
def main (argv):
    parser = argparse.ArgumentParser(description="AD9548 clock distribution tool")
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
        ('free-run', None, [], """Force device into free runing mode"""),
        ('holdover', None, [], """Force device into holdover mode"""),
        ("tuning", float, [], """Set new free running tuning word [Hz]"""),
        ("tuning-apply", None, [], """Apply new tuning word"""),
        ("pull-in-low", int, [], """Set lower pull-in range limit [binary mask].
        Limits the DDS tuning range"""),
        ("pull-in-high", int, [], """Set high pull-in range limit [binary mask].
        Limits the DDS tuning range"""),
        ('open-offset', float, [], u"""Open Loop phase offset in [%% of \u03A0 radians]"""),
        ('lock-offset', float, [], """Fixed phase locked offset in [s]"""),
        ('inc-step-size', float, [], """Phase lock offset incremental step size in [sec/step]"""),
        ('phase-slew-limit', float, [], """Set phase slew limit in [s/s]"""),
        ('history-acc-timer', float, [], """Set history accumulation timer, in [s]"""),
        ('single-sample-fallback', None, [], """When `single-sample fallback` is activated,
        the last tuning word from DPLL is used when word history is not available."""),
        ('persistent-history', None, [], """When persistent history is selected,
        the previous tuning word history is retained when switching to a new reference"""),
        ('k', int, range(8), """Set K value in Tavg/2^k formula for holdover history calculation spacing
        in time. Refer to official documentation."""),
    ]
    
    for (v_label, v_type, v_choices, v_helper) in flags:
        if v_type is None:
            parser.add_argument(
                "--{}".format(v_label),
                action="store_true",
                help=v_helper,
            )
        else:
            if len(v_choices) > 0:
                parser.add_argument(
                    "--{}".format(v_label),
                    choices=v_choices,
                    type=v_type,
                    help=v_helper,
                )
            else:
                parser.add_argument(
                    "--{}".format(v_label),
                    type=v_type,
                    help=v_helper,
                )
    args = parser.parse_args(argv)
    # open device
    dev = AD9548(args.bus, int(args.address, 16))

    if args.free_run:
        r = dev.read_data(0x0A01)
        dev.write_data(0x0A01, r|0x02)
        dev.io_update()
        return 0 #special op
    if args.holdover:
        r = dev.read_data(0x0A01)
        dev.write_data(0x0A01, r|0x04)
        dev.io_update()
        return 0 #special op

    if args.tuning:
        value = int(args.tuning, 16)
        dev.write_data(0x0300, value & 0xFF)
        dev.write_data(0x0301, (value & 0xFF00)>>8)
        dev.write_data(0x0302, (value & 0xFF0000)>>16)
        dev.write_data(0x0303, (value & 0xFF000000)>>24)
        dev.write_data(0x0304, (value & 0xFF00000000)>>32)
        dev.write_data(0x0305, (value & 0xFF0000000000)>>40)
    if args.tuning_apply:
        dev.write_data(0x0306, 0x01)
    if args.pull_in_low:
        value = int(args.pull_in_low, 16)
        dev.write_data(0x0307, value & 0xFF) 
        dev.write_data(0x0308, (value & 0xFF00)>>8) 
        dev.write_data(0x0309, (value & 0xFF0000)>>16) 
    if args.pull_in_high:
        value = int(args.pull_in_high, 16)
        dev.write_data(0x030A, value & 0xFF) 
        dev.write_data(0x030B, (value & 0xFF00)>>8) 
        dev.write_data(0x030C, (value & 0xFF0000)>>16) 
    if args.open_offset:
        value = round(args.open_offset * math.pi /100 * pow(2,15))
        dev.write_data(0x030D, value & 0xFF) 
        dev.write_data(0x030E, (value & 0xFF00)>>8) 
    if args.lock_offset:
        value = round(args.lock_offset * pow(10,12))
        dev.write_data(0x030F, value & 0xFF) 
        dev.write_data(0x0310, (value & 0xFF00)>>8) 
        dev.write_data(0x0311, (value & 0xFF0000)>>16) 
        dev.write_data(0x0312, (value & 0xFF0000)>>24) 
        dev.write_data(0x0313, (value & 0xFF0000)>>32) 
    if args.inc_step_size:
        value = round(args.inc_step_size * pow(10,12))
        dev.write_data(0x0314, value & 0xFF)
        dev.write_data(0x0315, (value & 0xFF00)>>8)
    if args.phase_slew_limit:
        value = round(args.phase_slew_limit * pow(10,9))
        dev.write_data(0x0316, value & 0xFF)
        dev.write_data(0x0317, (value & 0xFF00)>>8)
    if args.history_acc_timer:
        value = round(args.history_acc_timer * pow(10,3))
        dev.write_data(0x0318, value & 0xFF)
        dev.write_data(0x0319, (value & 0xFF00)>>8)
        dev.write_data(0x031A, (value & 0xFF0000)>>16)
    r = dev.read_data(0x031B)
    if args.single_sample_fallback:
        dev.write_data(0x031B, r | 0x10)
    else:
        dev.write_data(0x031B, r & (0x10^0xFF)) # mask out
    if args.persistent_history:
        dev.write_data(0x031B, r | 0x08)
    else:
        dev.write_data(0x031B, r & (0x08^0xFF)) # mask out
    if args.k:
        dev.write_data(0x031B, r |(args.k & 0x07)) 
    dev.io_update()
if __name__ == "__main__":
    main(sys.argv[1:])
