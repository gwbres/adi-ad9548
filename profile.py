#! /usr/bin/env python3
#################################################################
# Guillaume W. Bres, 2022          <guillaume.bressaix@gmail.com>
#################################################################
# profile.py
# Profile reader and designer (loader) 
# AD9547,48 supports up to 8 profiles
#################################################################
import sys
import math
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

def quantize_alpha (alpha):
    w = -math.ceil(math.log2(alpha)) if alpha < 1 else 0
    a1 = min(63, max(0, w)) if alpha < 1 else 0
    x = math.ceil(math.log2(alpha)) if alpha > 1 else 0
    y = min(22, max(0,x)) if alpha > 1 else 0
    a2 = 7 if y >= 8 else y
    a3 = y-7 if y >= 8 else 0
    z = round(alpha * pow(2,16+a1-a2-a3))
    a0 = min(65535, max(1,z))
    return (a0,a1,a2,a3)

def alpha (a0, a1, a2, a3):
    return  a0 * pow(2, -16+a1+a2+a3)

def quantize_beta (beta):
    x = -math.ceil(math.log2(abs(beta)))
    b1 = min(31, max(0, x))
    y = round(abs(beta) * pow(2,17+b1))
    b0 = min(131071, max(1,y))
    return (b0,b1)

def beta (d0, d1):
    return d0 * pow(2,-15 - d1)

def gamma (g0, g1):
    return beta(g0,g1)

def quantize_delta (delta):
    x = -math.ceil(math.log2(delta))
    d1 = min(31, max(0, x))
    y = round(delta * pow(2,15+b1))
    d0 = min(32767, max(1,y))
    return (d0,d1)

def quantize (value, q):
    if q == 'alpha':
        return quantize_alpha(value)
    elif q == 'delta':
        return quantize_delta(value)
    else:
        return quantize_beta(value)

def main (argv):
    parser = argparse.ArgumentParser(description="AD9548/47 profile tool")
    parser.add_argument(
        "bus",
        help="I2C bus",
    )
    parser.add_argument(
        "address",
        help="I2C slv address",
    )
    parser.add_argument(
        "profile",
        type=int,
        help="Select internal profile",
    )
    parser.add_argument(
        '--load',
        action="store_true",
        help='Load a profile',
    )
    parser.add_argument(
        '--read',
        action="store_true",
        help='Read current profile',
    )
    flags = [
        ("period", float, "Reference period [s]"),
        ("inner", float, "inner tolerance [ppm]"),
        ("outter", float, "outter tolerance [ppm]"),
        ("validation", float, "validation timer [s]"),
        ("redetect", float, "redetect timer [s]"),
        ("alpha", float, "Filter alpha coefficient"),
        ("beta", float, "Filter beta coefficient"),
        ("delta", float, "Filter delta coefficient"),
        ("gamma", float, "Filter gamma coefficient"),
    ]
    for (v_flag, v_type, v_helper) in flags:
        parser.add_argument(
            "--{}".format(v_flag),
            type=v_type,
            help=v_helper)
    args = parser.parse_args(argv)

    # open device
    handle = SMBus()
    #handle.open(int(args.bus))
    #address = int(args.address, 16)
    profile = int(args.profile)

    base = 0x0601 
    size = 0x0631 - base
    base = base + size * args.profile

    if args.read:
        profile = {}
        per  = read_data(handle, address, base +0)
        per += read_data(handle, address, base +1) <<8
        per += read_data(handle, address, base +2) <<16
        per += read_data(handle, address, base +3) <<24
        per += read_data(handle, address, base +4) <<32
        per += read_data(handle, address, base +5) <<40
        per += (read_data(handle, address, base +6) & 0x3) <<48
        profile['period'] = per * 1E-15
        inner  = read_data(handle, address, base +7)
        inner += read_data(handle, address, base +8) << 8
        inner += (read_data(handle, address, base +9) & 0x0F) << 8
        profile['inner'] = inner
        inner  = read_data(handle, address, base +10)
        inner += read_data(handle, address, base +11) << 8
        inner += (read_data(handle, address, base +12) & 0x0F) << 8
        profile['outter'] = inner
        timer  = read_data(handle, address, base +13)
        timer += read_data(handle, address, base +14) << 8
        profile['validation'] = timer *1E-3
        timer  = read_data(handle, address, base +15)
        timer += read_data(handle, address, base +16) << 8
        profile['redetect'] = timer *1E-3
        a0  = read_data(handle, address, base +17)
        a0 += read_data(handle, address, base +18) << 8
        a  = read_data(handle, address, base +19)
        a1 = a & 0x1F
        a2 = (a & 0xC0)>>6
        b  = read_data(handle, address, base +20)
        a2 += (b & 0x01) << 2
        b0 = (b & 0xFE)>>1
        b0 += read_data(handle, address, base +21) << 8
        r = read_data(handle, address, base +22)
        b0 += (r & 0x03) << 16
        b1 = (r & 0x7C)>>2
        g0 = read_data(handle, address, base +23)
        g0 += read_data(handle, address, base +24) << 8
        r = read_data(handle, address, base +25)
        g0 += (r&0x01) << 16
        g1 = (r&0x3E) >> 1
        d0 = read_data(handle, address, base+26)
        r = read_data(handle, address, base+27)
        d0 += (r&0x7F) << 8
        d1 = ((r & 0x80) >> 7) << xxxx
        r = read_data(handle, address, base+28)
        d1 += (r & 0x0F) << 1
        a3 = (r & 0xF0)>>4
        profile['alpha'] = alpha(a0,a1,a2,a3)
        profile['beta'] = beta(b0,b1)
        profile['delta'] = delta(d0,d1)
        profile['gamma'] = gamma(g0,g1)
        pprint(profile)
        return 0

    if args.period:
        if args.load:
            per = round(args.period * 1E15)
            write_data(handle, address, base +0, per & 0xFF)
            write_data(handle, address, base +1, (per & 0xFF00)>>8)
            write_data(handle, address, base +2, (per & 0xFF0000)>>16)
            write_data(handle, address, base +3, (per & 0xFF000000)>>24)
            write_data(handle, address, base +4, (per & 0xFF00000000)>>32)
            write_data(handle, address, base +5, (per & 0xFF0000000000)>>40)
            write_data(handle, address, base +7, (per & 0xFF000000000000)>>48)

    if args.alpha:
        if args.load:
            q = quantize(args.alpha, 'alpha')
            print(u'Quantized \u03B1', q)
    if args.beta:
        if args.load:
            q = quantize(args.beta, 'beta')
            print(u'Quantized \u03B2', q)
            #write_data (handle, address, 0x0612)
    if args.delta:
        if args.load:
            q = quantize(args.delta, 'delta')
            print(u'Quantized \u03B4', q)
    if args.gamma:
        if args.load:
            q = quantize(args.gamma, 'gamma')
            print(u'Quantized \u03B3', q)
    write_data(handle, address, 0x0005, 0x01) # i/o update
if __name__ == "__main__":
    main(sys.argv[1:])
