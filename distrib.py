#! /usr/bin/env python3
#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# distrib.py: AD9548 clock distribution management
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
    parser = argparse.ArgumentParser(description="AD9548 clock distribution tool")
    parser.add_argument(
        "bus",
        help="I2C bus",
    )
    parser.add_argument(
        "address",
        help="I2C slv address",
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
    handle = SMBus()
    handle.open(int(args.bus))
    address = int(args.address, 16)

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

    if args.source: # special op
        r = read_data(handle, address, 0x0402)
        write_data(handle, address, 0x0402, r | (sources[args.source]) << 4)
        write_data(handle, address, 0x0005, 0x01) # IO update
        return 0
    if args.autosync: # special op
        write_data(handle, address, 0x0403, autosync[args.autosync]) 
        write_data(handle, address, 0x0005, 0x01) # IO update
        return 0
   
    if args.divider: # Qx DIV
        if args.channel == 'all':
            bases = [0x0408, 0x040C, 0x0410, 0x0414]
        else:
            bases = [0x0408 + int(args.channel)*4]
        for base in bases:
            write_data(handle, address, base+0, args.divider & 0xFF) 
            write_data(handle, address, base+1, (args.divider & 0xFF00)>>8)
            write_data(handle, address, base+2, (args.divider & 0xFF0000)>>16)
            write_data(handle, address, base+3, (args.divider & 0xF000000)>>24)
        write_data(handle, address, 0x0005, 0x01) # IO update
        return 0
    
    # other op
    if args.channel == 'all':
        bases = [0x0404, 0x0405, 0x046, 0x047]
    else:
        bases = [0x0408 + int(args.channel)]

    for base in bases:
        r = read_data(handle, address, base)
        if args.cmos_phase:
            r |= phase[args.cmos_phase] << 5
        if args.polarity:
            r |= polarity[args.polarity] << 4
        if args.strength:
            r |= strengths[args.strength] << 3
        if args.mode:
            r |= modes[args.mode]
        write_data(handle, address, base, r)
    write_data(handle, address, 0x0005, 0x01) # IO update
if __name__ == "__main__":
    main(sys.argv[1:])
