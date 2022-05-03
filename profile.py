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
import json
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
    parser = argparse.ArgumentParser(description="AD9548 profile tool")
    parser.add_argument(
        "bus",
        metavar="bus",
        help="I2C bus",
    )
    parser.add_argument(
        "address",
        metavar="address",
        help="I2C slv address",
    )
    parser.add_argument(
        '--load',
        metavar="profile",
        type=int,
        choices=range(8),
        help='Load settings into internal profile',
    )
    parser.add_argument(
        '--read',
        metavar="profile",
        type=int,
        choices=range(8),
        help='Read internal profile content',
    )
    flags = [
        ("freq", float, "Read/Set reference frequency [Hz] for given profile"),
        ("inner", float, "Read/Set inner tolerance [ppm]"),
        ("outter", float, "Read/Set, outter tolerance [ppm]"),
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
    handle.open(int(args.bus))
    address = int(args.address, 16)

    reg0 = 0x0601 
    size = 0x0631 - reg0 

    if args.read:
        base = reg0 + size * args.read
        print("debug: base_address is {}".format(hex(base)))
        profile = {}
        per  = read_data(handle, address, base +0)
        per += read_data(handle, address, base +1) <<8
        per += read_data(handle, address, base +2) <<16
        per += read_data(handle, address, base +3) <<24
        per += read_data(handle, address, base +4) <<32
        per += read_data(handle, address, base +5) <<40
        per += (read_data(handle, address, base +6) & 0x3) <<48
        profile['freq'] = 1.0/(per * 1E-15)
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

        div  = read_data(handle, address, base + 0x61E - reg0)
        div += read_data(handle, address, base + 0x61F - reg0) << 8
        div += read_data(handle, address, base + 0x620 - reg0) << 16
        div += (read_data(handle, address, base + 0x621 - reg0) & 0x1F) << 24
        profile['r-div'] = div
        
        div  = read_data(handle, address, base + 0x622 - reg0)
        div += read_data(handle, address, base + 0x623 - reg0) << 8
        div += read_data(handle, address, base + 0x624 - reg0) << 16
        div += (read_data(handle, address, base + 0x625 - reg0) & 0x1F) << 24
        profile['s-div'] = div

        profile['fractionnal-div'] = {}
        r0 = read_data(handle, address, base + 0x0626 - reg0)
        r1 = read_data(handle, address, base + 0x0627 - reg0)
        r2 = read_data(handle, address, base + 0x0628 - reg0)
        V = r0
        V += (r1 & 0x03)<<8
        U = (r1 & 0xF0)>>4
        U += (r2 & 0x1F)<<4
        profile['fractionnal-div']['U'] = U
        profile['fractionnal-div']['V'] = V

        print(json.dumps(profile, sort_keys=True, indent=2))
        return 0

    profile = args.load
    base = reg0 + size * args.load
    print("debug: base_address is {}".format(hex(base)))
    
    if args.freq:
        per = round(1E15/args.freq)
        write_data(handle, address, base +0, per & 0xFF)
        write_data(handle, address, base +1, (per & 0xFF00)>>8)
        write_data(handle, address, base +2, (per & 0xFF0000)>>16)
        write_data(handle, address, base +3, (per & 0xFF000000)>>24)
        write_data(handle, address, base +4, (per & 0xFF00000000)>>32)
        write_data(handle, address, base +5, (per & 0xFF0000000000)>>40)
        write_data(handle, address, base +7, (per & 0xFF000000000000)>>48)

    if args.alpha:
        q = quantize(args.alpha, 'alpha')
        print(u'Quantized \u03B1', q)
        write_data(handle, address, base + 0x612-reg0, q[0] & 0xFF)
        write_data(handle, address, base + 0x613-reg0,(q[0] & 0xFF00)>>8)
        r = q[1] & 0x3F
        r |= (q[2] & 0x03) << 6
        write_data(handle, address, base + 0x614-reg0, r)
        r = read_data(handle, address, base +0x615-reg0)
        r |= (q[2] & 0x04)>>2
        write_data(handle, address, base + 0x615-reg0, r)

        r = read_data(handle, address, base + 0x061D-reg0)
        r |= (q[3] & 0x0F)<<4
        write_data(handle, address, base + 0x61D-reg0, r)

    if args.beta:
        q = quantize(args.beta, 'beta')
        print(u'Quantized \u03B2', q)
        r = read_data(handle, address, base + 0x615-reg0)
        r |= (q[0]&0x7F)<<1
        write_data(handle, address, base + 0x615-reg0, r)
        write_data(handle, address, base + 0x616-reg0, (q[0] & 0x7F8)>>7)

        r = (q[0] & 0x1800) >> 11
        r |= (q[1] & 0x1F)
        write_data(handle, address, base + 0x617-reg0, r)

    if args.gamma:
        q = quantize(args.gamma, 'gamma')
        print(u'Quantized \u03B3', q)
        write_data(handle, address, base + 0x618-reg0, q[0] & 0xFF)
        write_data(handle, address, base + 0x619-reg0, (q[0] & 0xFF00)>>8)
        
        r = read_data(handle, address, base + 0x061A-reg0)
        r =  (q[0] & 0x10000)>>16
        r |= (q[1] & 0x1F)<<1
        write_data(handle, address, base + 0x061A-reg0, r)

    if args.delta:
        q = quantize(args.delta, 'delta')
        print(u'Quantized \u03B4', q)

        write_data(handle, address, base + 0x061B-reg0, q[0] & 0xFF)
        r  = (q[0] & 0x7F00)>>8
        r |= (q[1] & 0x01)<<7
        write_data(handle, address, base + 0x061C-reg0, r)

        r = read_data(handle, address, base + 0x061D - reg0)

    write_data(handle, address, 0x0005, 0x01) # i/o update
if __name__ == "__main__":
    main(sys.argv[1:])
