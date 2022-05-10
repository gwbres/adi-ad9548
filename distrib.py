#! /usr/bin/env python3
#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# distrib.py: AD9548 clock distribution management
#################################################################
import sys
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
    parser.add_argument(
        "--channel",
        metavar="channel",
        choices=["0","1","2","3","all"],
        default="all",
        type=str,
        help="Select OUTx or Qx to configure. Defaults to `all`.",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="""Iniate a SYNC operation of the distribution stage manually"""
    )
    parser.add_argument(
        "--source",
        metavar="source",
        choices=["direct","active","dpll-feedback"],
        action="store_true",
        help="""Select the synchronization source for the clock distribution output channels.
        --channel is discarded in the special operation.""",
    )
    parser.add_argument(
        "--autosync",
        metavar="autosync",
        choices=["disabled","dpll-freq-lock","dpll-phase-lock"],
        help="""Select autosync mode/behavior""",
    )
    
    flags = [
        ("cmos-phase", str, ['normal','inverted'], """
        When the output mode is CMOS, this bit inverts the relative phase
        between the two CMOS output pins. Otherwise, this bit is discarded."""),
        ('polarity', str, ['normal','inverted'], """Set OUTx polarity"""),
        ('strength', str, ['low','normal'], """Select between low (LVDS 3.5mA output)[default] and
        normal (LVDS 7mA) output"""),
        ('mode', str, ['cmos','cmos+','trist+','trist','lvds','lvpecl'],
        """Select OUTx operating mode. CMOS (both pins), CMOS+: positive pin, tristate negative pin.
        Trist+: positive pin, CMOS negative pin. Trist: tristate (both pins) [default]."""),
        ('divider', int, [], "Set Qx division ratio"),
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
    dev = AD9548(args.bus, int(args.address,16))

    sources = {
        'direct': 0,
        'active': 1,
        'dpll-feedback': 2,
    }
    autosync = {
        'disabled': 0,
        'dpll-freq-lock': 1,
        'dpll-phase-lock': 2,
    }
    phase = {
        'normal': 0,
        'inverted': 1,
    }
    polarity = {
        'normal': 0,
        'inverted': 1,
    }
    strengths = {
        'low': 0,
        'normal': 1,
    }
    modes = {
        'cmos': 0,
        'cmos+': 1,
        'trist+': 2,
        'trist': 3,
        'lvds': 4,
        'lvpecl': 5,
    }

    if args.sync: # special op
        r = dev.read_data(0x0A02)
        dev.write_data(0x0A02, r | 0x02) # assert
        dev.io_update()
        dev.write_data(0x0A02, r & (0x02^0xFF)) # deassert 
        dev.io_update()
        return 0
    if args.source: # special op
        r = dev.read_data(0x0402)
        r &= 0xCF # mask out 
        dev.write_data(0x0402, r | (sources[args.source]) << 4)
        dev.io_update()
        return 0
    if args.autosync: # special op
        r = dev.read_data(0x0403)
        r &= 0xFC # mask out
        dev.write_data(0x0403, r | autosync[args.autosync])
        dev.io_update()
        return 0
   
    if args.divider: # Qx DIV
        if args.channel == 'all':
            bases = [0x0408, 0x040C, 0x0410, 0x0414]
        else:
            bases = [0x0408 + int(args.channel)*4]
        for base in bases:
            dev.write_data(base+0, args.divider & 0xFF)
            dev.write_data(base+1, (args.divider & 0xFF00)>>8)
            dev.write_data(base+2, (args.divider & 0xFF0000)>>16)
            dev.write_data(base+3, (args.divider & 0x3F000000)>>24)
        dev.io_update()
        return 0
    
    # other op
    if args.channel == 'all':
        bases = [0x0404, 0x0405, 0x046, 0x047]
    else:
        bases = [0x0408 + int(args.channel)]

    for base in bases:
        r = dev.read_data(base)
        if args.cmos_phase:
            r &= 0xDF # mask bit out
            r |= phase[args.cmos_phase] << 5
        if args.polarity:
            r &= 0xEF # mask bit out
            r |= polarity[args.polarity] << 4
        if args.strength:
            r &= 0xFE # mask bit out
            r |= strengths[args.strength] << 3
        if args.mode:
            r &= 0xF8 # mask bits out
            r |= modes[args.mode]
        dev.write_data(base, r)
    dev.io_update()
if __name__ == "__main__":
    main(sys.argv[1:])
